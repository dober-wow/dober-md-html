"""
Command-line interface for md2html converter.
Explicit configuration, no fallbacks, no magic.
"""

import logging
import sys
from pathlib import Path
import click

from .converter import convert_markdown, convert_directory
from .watcher import watch_directory
from .server import serve_directory

# Configure logging
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='2.0.0', prog_name='md2html')
@click.option('--log-level', default='INFO',
              type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Set logging level')
def cli(log_level):
    """
    Markdown to HTML converter.
    
    Explicit configuration only. No fallbacks, no auto-detection.
    All options must be specified.
    """
    # Configure logging based on user preference
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.debug(f"Logging level set to: {log_level}")


@cli.command()
@click.argument('source', type=click.Path(exists=True, readable=True))
@click.option('--output', '-o', required=True, type=click.Path(),
              help='Output path (required)')
@click.option('--theme', '-t', 
              type=click.Choice(['manaforge', 'github', 'minimal', 'dark']),
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
            logger.info(f"Starting single file conversion: {source_path}")
            convert_markdown(source_path, output_path, theme, embed_images, toc)
            click.echo(f"Success: {output_path}")
            logger.info(f"Successfully converted to: {output_path}")
        except Exception as e:
            logger.error(f"Conversion failed: {e}", exc_info=True)
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    
    elif source_path.is_dir():
        if output_path.exists() and output_path.is_file():
            click.echo(f"Error: Output must be a directory when source is a directory", err=True)
            sys.exit(1)
        
        # Convert directory
        try:
            click.echo(f"Converting directory: {source_path}")
            logger.info(f"Starting directory conversion: {source_path}")
            count = convert_directory(source_path, output_path, theme, embed_images, toc, recursive)
            click.echo(f"Success: Converted {count} files to {output_path}")
            logger.info(f"Batch conversion complete: {count} files")
        except Exception as e:
            logger.error(f"Directory conversion failed: {e}", exc_info=True)
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
              type=click.Choice(['manaforge', 'github', 'minimal', 'dark']),
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
    logger.info(f"Starting file watcher on: {dir_path}")
    
    try:
        watch_directory(dir_path, out_path, theme, interval, recursive)
    except KeyboardInterrupt:
        logger.info("File watcher stopped by user")
        click.echo("\nStopped watching.")
    except Exception as e:
        logger.error(f"Watch mode failed: {e}", exc_info=True)
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
        logger.error(f"No HTML files found in {dir_path}")
        click.echo(f"Error: No HTML files found in {dir_path}", err=True)
        sys.exit(1)
    
    logger.info(f"Found {len(html_files)} HTML files to serve")
    
    click.echo(f"Serving: {dir_path}")
    click.echo(f"URL: http://{host}:{port}")
    click.echo(f"Press Ctrl+C to stop")
    logger.info(f"Starting HTTP server on {host}:{port}")
    
    try:
        serve_directory(dir_path, host, port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        click.echo("\nServer stopped.")
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()