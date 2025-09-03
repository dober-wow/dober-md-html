"""
md2html - Ultra-clean Markdown to HTML converter
No magic, no fallbacks, explicit configuration only.
"""

__version__ = "2.0.0"
__author__ = "Bean Raid"

from .cli import cli
from .converter import convert_markdown

__all__ = ['cli', 'convert_markdown', '__version__']