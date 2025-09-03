"""
File watcher for automatic markdown conversion.
No auto-detection, explicit configuration only.
"""

import time
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .converter import convert_markdown


class MarkdownHandler(FileSystemEventHandler):
    """
    Handle file system events for markdown files.
    No fallbacks, explicit paths only.
    """
    
    def __init__(self, source_dir: Path, output_dir: Path, theme: str, recursive: bool):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.theme = theme
        self.recursive = recursive
        self.last_processed = {}
        
    def should_process(self, path: Path) -> bool:
        """Check if file should be processed. No magic."""
        # Must be markdown file
        if path.suffix not in ['.md', '.markdown']:
            return False
        
        # Check if in scope
        if not self.recursive:
            # Only process files in root directory
            if path.parent != self.source_dir:
                return False
        
        # Debounce - don't process same file within 1 second
        now = time.time()
        last = self.last_processed.get(str(path), 0)
        if now - last < 1.0:
            return False
        
        self.last_processed[str(path)] = now
        return True
    
    def on_modified(self, event):
        """Handle file modification. No recovery on errors."""
        if event.is_directory:
            return
        
        path = Path(event.src_path)
        
        if not self.should_process(path):
            return
        
        # Calculate output path
        rel_path = path.relative_to(self.source_dir)
        output_path = self.output_dir / rel_path.with_suffix('.html')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Converting: {path.name}")
        
        try:
            convert_markdown(
                path,
                output_path,
                self.theme,
                embed_images=True,  # Always embed in watch mode
                toc=False  # No TOC in watch mode
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Success: {output_path.name}")
        except Exception as e:
            # Report error but continue watching
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
    
    def on_created(self, event):
        """Handle new file creation."""
        self.on_modified(event)


def watch_directory(
    source_dir: Path,
    output_dir: Path,
    theme: str,
    interval: float,
    recursive: bool
) -> None:
    """
    Watch directory for markdown file changes.
    No auto-detection, explicit configuration only.
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    if not source_dir.is_dir():
        raise ValueError(f"Not a directory: {source_dir}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up file watcher
    event_handler = MarkdownHandler(source_dir, output_dir, theme, recursive)
    observer = Observer()
    observer.schedule(event_handler, str(source_dir), recursive=recursive)
    
    # Start watching
    observer.start()
    
    try:
        while True:
            time.sleep(interval)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()