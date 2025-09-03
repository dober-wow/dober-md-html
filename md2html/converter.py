"""
Core markdown to HTML conversion.
No fallbacks, no auto-detection, explicit configuration only.
"""

import base64
import mimetypes
from pathlib import Path
from typing import Optional

import markdown
from bs4 import BeautifulSoup


def load_theme(theme_name: str) -> str:
    """
    Load theme CSS. No fallbacks, no searching.
    Theme must exist in themes/ directory.
    """
    theme_path = Path(__file__).parent / 'themes' / f'{theme_name}.css'
    
    if not theme_path.exists():
        raise FileNotFoundError(f"Theme not found: {theme_name}")
    
    return theme_path.read_text(encoding='utf-8')


def encode_image(image_path: Path) -> str:
    """
    Encode image to base64 data URI.
    No fallback MIME types, must be detectable.
    """
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"Not a valid image file: {image_path}")
    
    with open(image_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    
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
        raise FileNotFoundError(f"Markdown file not found: {md_file}")
    
    if not md_file.suffix in ['.md', '.markdown']:
        raise ValueError(f"Not a markdown file: {md_file}")
    
    # Read markdown content - UTF-8 only
    try:
        content = md_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        raise ValueError(f"File is not valid UTF-8: {md_file}")
    
    # Convert markdown to HTML with explicit extensions
    extensions = ['extra', 'codehilite']
    if toc:
        extensions.append('toc')
    
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(content)
    
    # Process images - no fallbacks
    html_content = process_images(html_content, md_file.parent, embed_images)
    
    # Load theme - must exist
    css = load_theme(theme)
    
    # Build final HTML
    final_html = build_html(html_content, css, md_file.stem)
    
    # Create output directory if needed
    html_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output file
    html_file.write_text(final_html, encoding='utf-8')


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
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_dir.is_dir():
        raise ValueError(f"Not a directory: {source_dir}")
    
    # Find markdown files
    pattern = '**/*.md' if recursive else '*.md'
    md_files = list(source_dir.glob(pattern))
    
    if not md_files:
        raise ValueError(f"No markdown files found in {source_dir}")
    
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
            raise RuntimeError(f"Failed to convert {md_file}: {e}")
    
    return count