"""
Simple HTTP server for previewing HTML files.
No conversion, no magic, just serving files.
"""

import asyncio
from pathlib import Path
from aiohttp import web


async def handle_file(request):
    """
    Serve HTML files from directory.
    No directory listing, explicit file requests only.
    """
    base_dir = request.app['base_dir']
    
    # Get requested path
    path = request.match_info.get('path', 'index.html')
    
    # Security: prevent directory traversal
    if '..' in path:
        raise web.HTTPForbidden(text="Invalid path")
    
    # Build full path
    file_path = base_dir / path
    
    # Default to index.html for directories
    if file_path.is_dir():
        file_path = file_path / 'index.html'
    
    # File must exist
    if not file_path.exists():
        raise web.HTTPNotFound(text=f"File not found: {path}")
    
    # Only serve HTML, CSS, JS, and images
    allowed_suffixes = {'.html', '.htm', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg'}
    if file_path.suffix.lower() not in allowed_suffixes:
        raise web.HTTPForbidden(text=f"File type not allowed: {file_path.suffix}")
    
    # Serve the file
    return web.FileResponse(file_path)


def serve_directory(directory: Path, host: str, port: int) -> None:
    """
    Start HTTP server to serve HTML files.
    No auto-reload, no conversion, just serving.
    """
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    
    # Create web application
    app = web.Application()
    app['base_dir'] = directory
    
    # Add routes
    app.router.add_get('/', handle_file)
    app.router.add_get('/{path:.*}', handle_file)
    
    # Run server
    web.run_app(app, host=host, port=port, print=None)


if __name__ == '__main__':
    # Test server
    import sys
    if len(sys.argv) > 1:
        serve_directory(Path(sys.argv[1]), '127.0.0.1', 8000)