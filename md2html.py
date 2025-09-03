#!/usr/bin/env python3
"""
md2html - Markdown to HTML converter
Entry point for the application.
"""

import sys
from pathlib import Path

# Check Python version - require 3.9+
if sys.version_info < (3, 9):
    print("Error: Python 3.9 or higher is required", file=sys.stderr)
    sys.exit(1)

# Check required dependencies
try:
    import click
    import markdown
    import bs4
    import watchdog
    import aiohttp
except ImportError as e:
    print(f"Error: Missing required dependency: {e.name}", file=sys.stderr)
    print("Install with: pip install click markdown beautifulsoup4 watchdog aiohttp", file=sys.stderr)
    sys.exit(1)

# Import and run CLI
from md2html.cli import cli

if __name__ == '__main__':
    cli()