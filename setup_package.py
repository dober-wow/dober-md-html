"""Setup script to copy all md2html files to the package directory"""
import shutil
import os
from pathlib import Path

# Source and destination paths
src_base = Path(r"K:\Bean_Raid")
dst_base = Path(r"K:\Bean_Raid\dober-md-html")

# Create necessary directories
(dst_base / "md2html" / "themes").mkdir(parents=True, exist_ok=True)

# Files to copy
files_to_copy = [
    # Python module files
    ("md2html/__init__.py", "md2html/__init__.py"),
    ("md2html/cli.py", "md2html/cli.py"),
    ("md2html/converter.py", "md2html/converter.py"),
    ("md2html/watcher.py", "md2html/watcher.py"),
    ("md2html/server.py", "md2html/server.py"),
    
    # Theme files
    ("md2html/themes/manaforge.css", "md2html/themes/manaforge.css"),
    ("md2html/themes/github.css", "md2html/themes/github.css"),
    ("md2html/themes/minimal.css", "md2html/themes/minimal.css"),
    ("md2html/themes/dark.css", "md2html/themes/dark.css"),
    
    # Main entry point
    ("md2html.py", "md2html.py"),
    
    # PowerShell wrapper
    ("Convert-MdBatch.ps1", "Convert-MdBatch.ps1"),
    
    # Requirements
    ("requirements.txt", "requirements.txt"),
]

# Copy each file
for src_file, dst_file in files_to_copy:
    src_path = src_base / src_file
    dst_path = dst_base / dst_file
    
    if src_path.exists():
        print(f"Copying {src_file}...")
        shutil.copy2(src_path, dst_path)
    else:
        print(f"Warning: {src_file} not found")

print("Package setup complete!")