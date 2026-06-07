# utils/text_editor — Multi-tab Text Editor

A lightweight, dark-themed text editor built on `tkinter`.  Designed for
quickly viewing and navigating project files, especially XML reports.

## Requirements

Python 3.10+ (standard library only — no extra packages).

## Launch

```bash
# Open blank (session is restored automatically)
python utils/text_editor/editor.py

# Open specific files
python utils/text_editor/editor.py path/to/file.xml another.txt
```

## Features

### Tabs

- Up to **10 tabs** open at once.  Attempting to open an 11th shows a warning.
- Each tab shows the **filename** as its label.
- **Close** a tab: right-click the tab → *Close Tab*, or press **Ctrl+W**.
- Unsaved changes are **silently discarded** on close — there is no save
  prompt.  The editor is intentionally read-focused; use your normal editor
  for writing.

### Session restore

On every launch the editor reopens the files that were open when it last
closed, at the same zoom level.  Session state is stored in:

```
~/.gfl2_text_editor_session.json
```

Files that no longer exist are silently skipped.

### Zoom

Zoom applies to **all open tabs** simultaneously.

| Action | Effect |
|--------|--------|
| **Ctrl + =** or **Ctrl + +** | Zoom in |
| **Ctrl + −** | Zoom out |
| **Ctrl + 0** | Reset to default (11 pt) |
| **Ctrl + scroll wheel** | Zoom in / out |

Range: 6 pt – 48 pt, in steps of 2 pt.  Current size is shown in the status bar.

### Status bar

The bar at the bottom of the window shows:
- Full path of the active file
- Cursor line and column (`Ln N, Col N`)
- Current font size

### XML support

Files with a `.xml` extension receive extra treatment automatically.

#### Syntax highlighting

| Element | Colour |
|---------|--------|
| Tag names | Blue |
| Attribute names | Light blue |
| Attribute values | Orange |
| Comments `<!-- -->` | Green (italic) |
| CDATA sections | Yellow |
| Processing instructions / DOCTYPE | Purple |
| Entity references `&amp;` | Teal |
| Angle brackets | Gray |

#### Node folding

A **▼ / ▶** marker appears in the line-number gutter next to every XML
element whose content spans more than one line.

- **▼** — element is expanded (click to collapse)
- **▶** — element is collapsed (click to expand)

Folding uses tkinter's native `elide` feature: the content is hidden but
never removed from the buffer, so folding and unfolding is instantaneous
and lossless.

> **Note:** fold markers are detected when the file loads.  Editing the
> file after load may cause markers to desync; reload (close and reopen
> the tab) to refresh them.

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file(s) |
| Ctrl+W | Close current tab |
| Ctrl+Q | Quit |
| Ctrl+= / Ctrl++ | Zoom in |
| Ctrl+− | Zoom out |
| Ctrl+0 | Reset zoom |
| Ctrl+scroll | Zoom in / out |
| Ctrl+Z / Ctrl+Y | Undo / Redo (standard text widget) |

## File layout

```
utils/text_editor/
├── editor.py     Main script (all logic in one file)
└── README.md     This file
```

Session state (`~/.gfl2_text_editor_session.json`) is written to the user's
home directory and can be safely deleted to reset the session.
