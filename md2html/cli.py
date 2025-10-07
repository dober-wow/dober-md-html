"""
Command-line interface for md2html converter.
Explicit configuration, no fallbacks, no magic.
"""

import sys
from pathlib import Path
import click

from .converter import convert_markdown, convert_directory
from .watcher import watch_directory
from .server import serve_directory

THEME_CHOICES = [
    'antorus',
    'dark',
    'emerald-nightmare',
    'github',
    'manaforge',
    'minimal',
    'nighthold',
    'tomb-of-sargeras',
    'trial-of-valor',
]


@click.group()
@click.version_option(version='2.0.0', prog_name='md2html')
def cli():
    """
    Markdown to HTML converter.
    
    Explicit configuration only. No fallbacks, no auto-detection.
    All options must be specified.
    """
    pass


@cli.command()
@click.argument('source', type=click.Path(exists=True, readable=True))
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output path (required)')
@click.option('--theme', '-t',
              type=click.Choice(THEME_CHOICES),
              required=True,
              help='Theme to use (required)')
@click.option('--embed-images/--link-images', default=True,
              help='Embed images as base64 (default: embed)')
@click.option('--toc/--no-toc', default=False,
              help='Generate table of contents (default: no)')
@click.option('--recursive/--no-recursive', default=False,
              help='Process subdirectories (default: no)')
def convert(source, output, theme, embed_images, toc, recursive):
    """
    Convert markdown files to HTML.
    
    All paths must be explicit. No auto-detection.
    """
    source_path = Path(source).resolve()
    output_path = Path(output).resolve()
    
    # Strict validation - no guessing
    if source_path.is_file():
        if not source_path.suffix in ['.md', '.markdown']:
            click.echo(f"Error: Not a markdown file: {source_path}", err=True)
            sys.exit(1)
        
        if output_path.is_dir() or output_path.suffix not in ['.html', '.htm']:
            click.echo(f"Error: Output must be an HTML file when source is a file", err=True)
            sys.exit(1)
        
        # Convert single file
        try:
            click.echo(f"Converting: {source_path}")
            convert_markdown(source_path, output_path, theme, embed_images, toc)
            click.echo(f"Success: {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    elif source_path.is_dir():
        if output_path.exists() and output_path.is_file():
            click.echo(f"Error: Output must be a directory when source is a directory", err=True)
            sys.exit(1)
        
        # Convert directory
        try:
            click.echo(f"Converting directory: {source_path}")
            count = convert_directory(source_path, output_path, theme, embed_images, toc, recursive)
            click.echo(f"Success: Converted {count} files to {output_path}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    else:
        click.echo(f"Error: Invalid source: {source_path}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, readable=True))
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output directory (required)')
@click.option('--theme', '-t',
              type=click.Choice(THEME_CHOICES),
              required=True,
              help='Theme to use (required)')
@click.option('--interval', type=float, default=1.0,
              help='Check interval in seconds (default: 1.0)')
@click.option('--recursive/--no-recursive', default=False,
              help='Watch subdirectories (default: no)')
def watch(directory, output, theme, interval, recursive):
    """
    Watch directory for changes and auto-convert.
    
    Output directory must be specified explicitly.
    """
    dir_path = Path(directory).resolve()
    out_path = Path(output).resolve()
    
    if not dir_path.exists():
        click.echo(f"Error: Directory not found: {dir_path}", err=True)
        sys.exit(1)
    
    click.echo(f"Watching: {dir_path}")
    click.echo(f"Output: {out_path}")
    click.echo(f"Theme: {theme}")
    click.echo(f"Press Ctrl+C to stop")
    
    try:
        watch_directory(dir_path, out_path, theme, interval, recursive)
    except KeyboardInterrupt:
        click.echo("\nStopped watching.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, readable=True))
@click.option('--port', '-p', type=int, default=8000,
              help='Port to serve on (default: 8000)')
@click.option('--host', '-h', default='127.0.0.1',
              help='Host to bind to (default: 127.0.0.1)')
def serve(directory, port, host):
    """
    Serve HTML files from directory.
    
    Directory must contain HTML files. No conversion performed.
    """
    dir_path = Path(directory).resolve()
    
    if not dir_path.exists():
        click.echo(f"Error: Directory not found: {dir_path}", err=True)
        sys.exit(1)
    
    # Check for HTML files
    html_files = list(dir_path.glob('**/*.html'))
    if not html_files:
        click.echo(f"Error: No HTML files found in {dir_path}", err=True)
        sys.exit(1)
    
    click.echo(f"Serving: {dir_path}")
    click.echo(f"URL: http://{host}:{port}")
    click.echo(f"Press Ctrl+C to stop")
    
    try:
        serve_directory(dir_path, host, port)
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
