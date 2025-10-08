"""
Core markdown to HTML conversion.
No fallbacks, no auto-detection, explicit configuration only.
"""

import base64
import logging
import mimetypes
import os
import re
from pathlib import Path
from typing import Optional

import markdown
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger(__name__)

# Configuration constants
MAX_IMAGE_SIZE_MB = 10  # Maximum image size in megabytes
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

AVAILABLE_THEMES = {
    'antorus',
    'dark',
    'emerald-nightmare',
    'github',
    'manaforge',
    'minimal',
    'nighthold',
    'tomb-of-sargeras',
    'trial-of-valor',
}
AVAILABLE_THEMES_LIST = sorted(AVAILABLE_THEMES)
THEME_HINT_COMMENT_RE = re.compile(
    r'<!--\s*md2html-theme\s*:\s*([a-z0-9\-]+)\s*-->',
    re.IGNORECASE,
)


def load_theme(theme_name: str) -> str:
    """
    Load theme CSS. No fallbacks, no searching.
    Theme must exist in themes/ directory.
    """
    theme_path = Path(__file__).parent / 'themes' / f'{theme_name}.css'
    
    if not theme_path.exists():
        logger.error(f"Theme not found: {theme_name} at {theme_path}")
        raise FileNotFoundError(f"Theme not found: {theme_name}")
    
    logger.debug(f"Loading theme: {theme_name} from {theme_path}")
    return theme_path.read_text(encoding='utf-8')


def _normalize_theme(theme: str, md_file: Path) -> str:
    candidate = theme.strip().strip('"').strip("'").lower()
    if not candidate:
        raise ValueError(f"Theme metadata in {md_file} is empty")
    if candidate not in AVAILABLE_THEMES:
        raise ValueError(
            f"Unknown theme '{candidate}' in {md_file}. "
            f"Available themes: {', '.join(AVAILABLE_THEMES_LIST)}"
        )
    return candidate


def _extract_theme_from_content(content: str, md_file: Path) -> Optional[str]:
    snippet = content[:2000]
    comment_match = THEME_HINT_COMMENT_RE.search(snippet)
    if comment_match:
        return _normalize_theme(comment_match.group(1), md_file)

    stripped = content.lstrip()
    if not stripped.startswith('---'):
        return None

    lines = stripped.splitlines()
    if not lines:
        return None

    front_matter: list[str] = []
    for line in lines[1:]:
        if line.strip() == '---':
            break
        front_matter.append(line.rstrip('\n'))

    idx = 0
    while idx < len(front_matter):
        raw_line = front_matter[idx]
        line = raw_line.strip()
        if not line or line.startswith('#'):
            idx += 1
            continue
        if ':' not in line:
            idx += 1
            continue

        key, value = line.split(':', 1)
        key = key.strip().lower()
        value = value.strip()

        if key in ('theme', 'md2html-theme'):
            return _normalize_theme(value, md_file)

        if key == 'md2html':
            idx += 1
            while idx < len(front_matter):
                sub_raw = front_matter[idx]
                if not sub_raw.startswith((' ', '\t')):
                    break
                sub_line = sub_raw.strip()
                if sub_line.startswith('theme:'):
                    _, sub_value = sub_line.split(':', 1)
                    return _normalize_theme(sub_value, md_file)
                idx += 1
            continue

        idx += 1

    return None


def _resolve_theme_choice(requested_theme: str, content: str, md_file: Path) -> str:
    discovered = _extract_theme_from_content(content, md_file)

    if requested_theme == 'auto':
        if discovered:
            logger.info("Detected theme '%s' for %s", discovered, md_file.name)
            return discovered
        raise ValueError(
            f"No theme metadata found in {md_file}. "
            "Specify a theme with --theme or add "
            "`<!-- md2html-theme: <theme> -->` or front matter."
        )

    if discovered and discovered != requested_theme:
        logger.info(
            "Applying per-file theme '%s' for %s (overriding CLI choice '%s')",
            discovered,
            md_file.name,
            requested_theme,
        )
        return discovered

    if requested_theme not in AVAILABLE_THEMES:
        raise ValueError(
            f"Unknown theme '{requested_theme}'. "
            f"Available themes: {', '.join(AVAILABLE_THEMES_LIST)}"
        )

    return requested_theme


def encode_image(image_path: Path) -> str:
    """
    Encode image to base64 data URI.
    No fallback MIME types, must be detectable.
    Includes size validation to prevent memory exhaustion.
    """
    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Check file size before processing
    file_size = image_path.stat().st_size
    if file_size > MAX_IMAGE_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        logger.warning(f"Image too large: {image_path.name} ({size_mb:.1f}MB)")
        raise ValueError(
            f"Image too large: {image_path.name} is {size_mb:.1f}MB "
            f"(max: {MAX_IMAGE_SIZE_MB}MB)"
        )
    
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"Not a valid image file: {image_path}")
    
    # Validate common image formats
    valid_formats = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 
        'image/svg+xml', 'image/webp', 'image/bmp'
    }
    if mime_type not in valid_formats:
        raise ValueError(
            f"Unsupported image format: {mime_type} for {image_path.name}"
        )
    
    with open(image_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    
    logger.debug(f"Encoded image: {image_path.name} ({file_size / 1024:.1f}KB)")
    return f"data:{mime_type};base64,{encoded}"


def process_images(html: str, base_dir: Path, embed: bool) -> str:
    """
    Process images in HTML. No path searching.
    Images must be relative to markdown file location.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    for img in soup.find_all('img'):
        src = img.get('src')
        
        if not src:
            raise ValueError("Image tag without src attribute found")
        
        # Skip external images
        if src.startswith(('http://', 'https://', 'data:')):
            continue
        
        # Image must be relative to markdown file
        image_path = base_dir / src
        
        if not image_path.exists():
            logger.error(f"Image not found during processing: {image_path}")
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if embed:
            img['src'] = encode_image(image_path)
    
    return str(soup)


def build_html(content: str, css: str, title: str) -> str:
    """
    Build complete HTML document.
    No templates, no options, single format only.
    """
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="markdown-container">
{content}
    </div>
</body>
</html>'''


def convert_markdown(
    md_file: Path,
    html_file: Path,
    theme: str,
    embed_images: bool,
    toc: bool
) -> None:
    """
    Convert single markdown file to HTML.
    No fallbacks, strict validation, explicit configuration.
    """
    # Validate input
    if not md_file.exists():
        logger.error(f"Markdown file not found: {md_file}")
        raise FileNotFoundError(f"Markdown file not found: {md_file}")

    if not md_file.suffix in ['.md', '.markdown']:
        raise ValueError(f"Not a markdown file: {md_file}")

    # Read markdown content - UTF-8 only
    try:
        content = md_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {md_file}")

    resolved_theme = _resolve_theme_choice(theme, content, md_file)
    logger.info(f"Converting: {md_file} -> {html_file} [theme={resolved_theme}]")

    # Convert markdown to HTML with explicit extensions
    extensions = ['extra', 'codehilite']
    if toc:
        extensions.append('toc')

    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(content)

    # Process images - no fallbacks
    html_content = process_images(html_content, md_file.parent, embed_images)

    # Load theme - must exist
    css = load_theme(resolved_theme)

    # Build final HTML
    final_html = build_html(html_content, css, md_file.stem)

    # Create output directory if needed
    html_file.parent.mkdir(parents=True, exist_ok=True)

    # Write output file
    html_file.write_text(final_html, encoding='utf-8')
    logger.info(f"Successfully converted: {md_file.name} ({len(final_html) / 1024:.1f}KB)")

def convert_directory(
    source_dir: Path,
    output_dir: Path,
    theme: str,
    embed_images: bool,
    toc: bool,
    recursive: bool
) -> int:
    """
    Convert all markdown files in directory.
    No smart detection, explicit paths only.
    """
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_dir.is_dir():
        raise ValueError(f"Not a directory: {source_dir}")
    
    # Find markdown files
    pattern = '**/*.md' if recursive else '*.md'
    md_files = list(source_dir.glob(pattern))
    
    if not md_files:
        logger.warning(f"No markdown files found in {source_dir}")
        raise ValueError(f"No markdown files found in {source_dir}")
    
    logger.info(f"Found {len(md_files)} markdown files to convert")
    
    # Convert each file
    count = 0
    for md_file in md_files:
        # Calculate output path - preserve structure
        rel_path = md_file.relative_to(source_dir)
        html_path = output_dir / rel_path.with_suffix('.html')
        
        try:
            convert_markdown(md_file, html_path, theme, embed_images, toc)
            count += 1
        except Exception as e:
            # Fail on first error - no recovery
            logger.error(f"Failed to convert {md_file}: {e}")
            raise RuntimeError(f"Failed to convert {md_file}: {e}")
    
    logger.info(f"Successfully converted {count} files")
    return count

