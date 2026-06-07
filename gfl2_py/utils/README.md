# utils/

Standalone GUI tools for the GFL2 project.  Each tool is self-contained
and can be launched independently.

| Tool | Description | Launch |
|------|-------------|--------|
| [text_editor](text_editor/README.md) | Multi-tab text editor with XML highlight & folding | `python utils/text_editor/editor.py [file ...]` |
| [image_comparer](image_comparer/README.md) | Side-by-side zoomable image viewer | `python -m utils.image_comparer [left.png]` |

All tools require **Python 3.10+** and use only standard-library tkinter unless
stated otherwise in the individual README.
