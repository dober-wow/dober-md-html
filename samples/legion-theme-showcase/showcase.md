# Legion Theme Showcase

Welcome to the Legion raid palette tour. Each theme emphasizes readable body copy, strong contrast, and restrained accents.

## Headings & Paragraphs

### Subtitle In Practice

Long-form paragraphs stay comfortable thanks to generous line height and balanced color contrast. Inline emphasis like *italics*, **bold**, and `code spans` should remain legible across all palettes.

## Lists & Callouts

> The Nightmare does not sleep. It waits. — Xavius

- Bullet items surface typical raid callouts.
- Secondary lines demonstrate rhythm and spacing.
- Links such as [Raid Chronicle](../index.html) inherit the theme accent.

1. Ordered steps keep numerals distinct.
2. Subsequent lines show vertical cadence.

## Code & Tables

```python
def fel_rift(dps, duration):
    """Simulate burst window throughput."""
    ramp = dps * 0.12
    return dps * duration + ramp
```

| Boss            | Phase | Notes               |
|-----------------|-------|---------------------|
| Nythendra       | 1     | Rot/Volatile         |
| Odyn            | 2     | Runic Brand dance    |
| Gul'dan         | 3     | Eye soak assignments |

---

Ready to review? Render this sample with any Legion theme:

```bash
md2html convert samples/legion-theme-showcase/showcase.md ^
  --output docs/themes/<theme>/index.html ^
  --theme <theme>
```
