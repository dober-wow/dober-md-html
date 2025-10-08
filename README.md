# MD2HTML - Markdown to HTML Converter

MD2HTML is a theme-aware Markdown to HTML converter with a concise CLI, watch mode, and preview server. Behaviour stays explicit—when a document omits theme metadata under `--theme auto`, we fall back to the default `manaforge` palette instead of guessing.

## Features

- Theme-aware rendering for core styles (manaforge, github, minimal, dark) and raid-inspired palettes (emerald-nightmare, trial-of-valor, nighthold, tomb-of-sargeras, antorus)
- Batch conversion for single files or entire directories with deterministic output
- Optional watch mode and lightweight HTTP server for rapid editing loops
- Image embedding with format and size validation to prevent surprises
- Metadata hook that picks a theme per document when running with --theme auto

## Installation

```bash
cd dober-md-html
pip install -r requirements.txt
```

Supported dependencies (Python 3.9+): markdown, beautifulsoup4, click, watchdog, aiohttp.

## Usage

### Convert a single file

```bash
python md2html.py convert README.md --output README.html --theme manaforge
```

### Convert a directory

```bash
python md2html.py convert repo/bean_raid --output docs --theme github --recursive
```

### Watch for changes

```bash
python md2html.py watch repo/bean_raid --output docs --theme dark --recursive
```

### Preview generated HTML

```bash
python md2html.py serve docs --port 8000
```

### PowerShell wrapper

```powershell
./Convert-MdBatch.ps1 -InputDir repo/bean_raid -OutputDir docs -Theme manaforge -Recursive
```

Add -Watch or -Serve -Port 3000 to mirror the CLI options.

## Automatic theme selection (--theme auto)

Running the converter with --theme auto (CLI) or -Theme auto (PowerShell) tells MD2HTML to read the desired theme from the markdown file. Declare the theme using either form:

1. Inline HTML comment (anywhere near the top):

   ```markdown
   <!-- md2html-theme: nighthold -->
   # Raid Log
   `

2. YAML front matter:

   ```markdown
   ---
   md2html:
     theme: trial-of-valor
   ---
   # Odyn Notes
   `

If --theme auto is used and no metadata exists, the converter prints a notice and converts with the default `manaforge` theme. Add metadata to opt into a different look per file.

## Theme catalogue

| Theme | Notes |
|-------|-------|
| manaforge | Dark UI with neon accents |
| github | GitHub-flavoured documentation |
| minimal | Light, distraction-free reading |
| dark | Classic dark reader |
| emerald-nightmare | Corrupted forest palette |
| `trial-of-valor` | Runic golden hall |
| `nighthold` | Arcane indigo and cyan |
| `tomb-of-sargeras` | Abyssal teal with fel fissures |
| `antorus` | Ember orange with fel sparks |

## GitHub Actions example

```yaml
name: Convert Markdown to HTML

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install markdown beautifulsoup4 click watchdog aiohttp

      - name: Convert markdown
        run: |
          # Use --theme auto when markdown files include theme metadata
          python md2html.py convert repo/bean_raid --output docs --theme auto --recursive

      - name: Upload artefacts
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs
```

## Project structure

```
dober-md-html/
|-- md2html/
|   |-- __init__.py
|   |-- cli.py
|   |-- converter.py
|   |-- server.py
|   |-- watcher.py
|   -- themes/
|       |-- manaforge.css
|       |-- github.css
|       |-- minimal.css
|       |-- dark.css
|       -- ...
|-- md2html.py
|-- Convert-MdBatch.ps1
|-- requirements.txt
|-- setup.py
-- README.md
```

## Configuration defaults

- **Theme**: Provide a name or use --theme auto; files without metadata fall back to `manaforge`
- **Output**: Always required
- **Recursive conversion**: Disabled by default (--recursive opt-in)
- **TOC generation**: Disabled by default (--toc to enable)
- **Image embedding**: Enabled by default (--link-images to disable)

## Contributing

Pull requests are welcome. Please keep the explicit-configuration philosophy intact.

## License

MIT License - see LICENSE.

## Support

Open an issue at https://github.com/dober-wow/dober-md-html/issues for questions or bug reports.
