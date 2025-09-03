# MD2HTML - Markdown to HTML Converter

A powerful, theme-based Markdown to HTML converter with live preview, file watching, and beautiful built-in themes.

## Features

- 🎨 **Beautiful Themes**: Manaforge (dark gaming), GitHub, Minimal, and Dark themes
- 📁 **Batch Conversion**: Convert single files or entire directories
- 👁️ **Live Preview**: Built-in server with auto-refresh
- 🔄 **File Watching**: Auto-convert on file changes
- 🖼️ **Image Handling**: Embed images as base64 or link them
- 📚 **Table of Contents**: Optional TOC generation
- 🚀 **Fast & Clean**: No magic, explicit configuration

## Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Requirements

- Python 3.9+
- markdown
- beautifulsoup4
- click
- watchdog
- aiohttp

## Usage

### Command Line Interface

#### Convert a Single File

```bash
python md2html.py convert input.md --output output.html --theme manaforge
```

#### Convert a Directory

```bash
python md2html.py convert docs/ --output site/ --theme github --recursive
```

#### Watch Mode

Automatically convert files when they change:

```bash
python md2html.py watch docs/ --output site/ --theme dark --recursive
```

#### Preview Server

Start a live preview server:

```bash
python md2html.py serve site/ --port 8000
```

### PowerShell Wrapper

For Windows users, use the PowerShell wrapper for easier batch operations:

```powershell
.\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme manaforge -Recursive
```

With live preview:

```powershell
.\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme dark -Serve -Port 3000
```

With file watching:

```powershell
.\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme github -Watch
```

## Themes

### Manaforge
A beautiful dark theme with blue/purple gradients, perfect for gaming and tech content.

### GitHub
Clean and familiar GitHub-style markdown rendering.

### Minimal
Simple, distraction-free reading experience.

### Dark
Classic dark mode for comfortable reading.

## Python API

```python
from md2html import convert_markdown

# Convert a single file
convert_markdown(
    input_path='README.md',
    output_path='README.html',
    theme='manaforge',
    embed_images=True,
    generate_toc=False
)
```

## GitHub Actions Integration

Use MD2HTML in your GitHub Actions workflow:

```yaml
name: Convert Markdown to HTML

on:
  push:
    branches: [main]

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install MD2HTML
        run: |
          pip install markdown beautifulsoup4 click watchdog aiohttp
          
      - name: Convert Markdown files
        run: |
          python md2html.py convert . --output _site --theme manaforge --recursive
          
      - name: Upload artifacts
        uses: actions/upload-pages-artifact@v3
        with:
          path: '_site'
```

## Project Structure

```
dober-md-html/
├── md2html/
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── converter.py      # Core conversion logic
│   ├── server.py         # Preview server
│   ├── watcher.py        # File watching
│   └── themes/           # CSS themes
│       ├── manaforge.css
│       ├── github.css
│       ├── minimal.css
│       └── dark.css
├── md2html.py            # Main entry point
├── Convert-MdBatch.ps1   # PowerShell wrapper
├── requirements.txt      # Python dependencies
├── setup.py             # Package setup
└── README.md            # This file
```

## Configuration

All configuration is explicit - no magic or auto-detection:

- **Theme**: Must be specified (no default)
- **Output**: Must be specified (no default)
- **Recursive**: Disabled by default (explicit opt-in)
- **TOC**: Disabled by default (explicit opt-in)
- **Image Embedding**: Enabled by default (can disable)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Author

Bean Raid

## Support

For issues, questions, or suggestions, please open an issue on GitHub:
https://github.com/dober-wow/dober-md-html/issues