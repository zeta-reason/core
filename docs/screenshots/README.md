# Zeta Reason Screenshots

This directory contains screenshots and visual documentation for Zeta Reason.

## Directory Structure

```
screenshots/
├── README.md                    # This file
├── main-interface.png           # Main application interface
├── summary-mode.png             # Summary Mode view
├── research-mode.png            # Research Mode view
├── experiment-history.png       # Experiment History sidebar
├── dark-mode.png                # Dark mode theme
├── model-configuration.png      # Model configuration interface
├── dataset-upload.png           # Dataset upload screen
├── metrics-cards.png            # Metric cards display
├── cot-viewer.png              # Chain-of-thought viewer
└── comparison-chart.png        # Multi-model comparison chart
```

## Screenshot Guidelines

### When Adding Screenshots

1. **Use consistent window size**: 1920x1080 or 1440x900
2. **Capture full context**: Include relevant UI elements
3. **Use sample data**: Avoid sensitive/proprietary data
4. **Show realistic scenarios**: Use meaningful examples
5. **Update regularly**: Keep in sync with UI changes

### Naming Convention

```
<feature>-<variant>.png

Examples:
- summary-mode-light.png
- summary-mode-dark.png
- research-mode-filtering.png
- experiment-history-open.png
```

### Format Requirements

- **Format**: PNG (lossless)
- **Max file size**: 2MB per image
- **Resolution**: At least 1440 width
- **Compression**: Use `pngcrush` or `optipng`

## Screenshots Needed

### Core Features

- [x] Main interface (with results)
- [ ] Empty state (no evaluation yet)
- [ ] Loading state (during evaluation)
- [ ] Error state (with error message)

### Summary Mode

- [ ] Metric cards (all metrics visible)
- [ ] Metrics table (single model)
- [ ] Metrics table (multi-model comparison)
- [ ] Metrics chart (bar chart)
- [ ] CoT viewer (expanded)
- [ ] Export menu

### Research Mode

- [ ] Task list (all tasks)
- [ ] Task list (filtered to errors)
- [ ] Task detail view (correct answer)
- [ ] Task detail view (incorrect answer)
- [ ] Multi-model comparison (side-by-side)
- [ ] Search functionality
- [ ] Filter controls

### Experiment History

- [ ] Sidebar (closed)
- [ ] Sidebar (open with experiments)
- [ ] Sidebar (empty state)
- [ ] Experiment card
- [ ] Delete confirmation

### Configuration

- [ ] Dataset upload (empty)
- [ ] Dataset upload (file selected)
- [ ] Dataset upload (validation error)
- [ ] Model configuration (single model)
- [ ] Model configuration (multiple models)
- [ ] Model presets dropdown
- [ ] Sampling configuration

### Themes

- [ ] Light mode (full interface)
- [ ] Dark mode (full interface)
- [ ] Theme toggle button

## Taking Screenshots

### macOS

1. **Full window**: `Cmd + Shift + 4` → `Space` → Click window
2. **Selected area**: `Cmd + Shift + 4` → Drag selection
3. **Full screen**: `Cmd + Shift + 3`

### Windows

1. **Full window**: `Alt + PrtScn`
2. **Full screen**: `PrtScn`
3. **Selected area**: `Win + Shift + S`

### Linux

1. **Full screen**: `PrtScn`
2. **Selected area**: `Shift + PrtScn`
3. **Window**: `Alt + PrtScn`

## Optimizing Screenshots

### Using `pngcrush`

```bash
pngcrush -brute input.png output.png
```

### Using `optipng`

```bash
optipng -o7 input.png
```

### Using ImageMagick (resize if needed)

```bash
convert input.png -resize 1440x900 output.png
```

## Using in Documentation

### Markdown

```markdown
![Main Interface](screenshots/main-interface.png)
```

### HTML (with sizing)

```html
<img src="screenshots/main-interface.png" alt="Main Interface" width="800">
```

### With captions

```markdown
![Main Interface](screenshots/main-interface.png)
*Figure 1: Zeta Reason main interface showing Summary Mode*
```

## Sample Data for Screenshots

### Use These Example Tasks

```jsonl
{"id": "1", "input": "What is 2+2?", "target": "4"}
{"id": "2", "input": "What is the capital of France?", "target": "Paris"}
{"id": "3", "input": "If x + 5 = 12, what is x?", "target": "7"}
```

### Use These Models

- **GPT-4** (OpenAI)
- **GPT-3.5-turbo** (OpenAI)
- **Dummy-Thinking** (Dummy provider)

### Configuration Examples

- Temperature: 0.7
- Max tokens: 1000
- CoT: Enabled
- Sampling: Random, 50 tasks

## Screenshot Checklist

Before adding a screenshot to the repository:

- [ ] Redacted any API keys or sensitive data
- [ ] Used sample/dummy data only
- [ ] Captured at appropriate resolution
- [ ] Optimized file size
- [ ] Named according to convention
- [ ] Updated this README if needed
- [ ] Verified image displays correctly in documentation

## Contributing Screenshots

To contribute screenshots:

1. Follow guidelines above
2. Add screenshots to this directory
3. Update this README
4. Create pull request with description

## Video Recordings

For animated demos, see [videos/README.md](../videos/README.md) (future).

Recommended format:
- MP4 or GIF
- Max 30 seconds per clip
- 1440x900 resolution
- Subtitles/annotations for clarity

---

## Current Status

**Last Updated:** January 2025
**Screenshot Coverage:** 0% (Placeholder only)

**Next Steps:**
1. Capture main interface screenshots
2. Add Summary Mode screenshots
3. Add Research Mode screenshots
4. Document all features visually

---

**Note:** This is a placeholder directory. Screenshots will be added as the application matures and UI stabilizes.
