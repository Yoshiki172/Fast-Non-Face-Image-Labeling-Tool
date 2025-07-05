# Fast Non-Face Image Labeling Tool

A lightweight, fast annotation GUI for images where standard face detectors fail. Ideal for quick bounding-box labeling of any object, not just faces.

## Features

- **Easy Folder Loading**: Select a directory of images and step through them with `Next`/`Prev` buttons.
- **Bounding-Box Drawing**: Click-and-drag to create rectangular or square regions; right-click to delete.
- **Grid Snap & Customizable Grid**: Overlay a grid (e.g. 64×32) on the image for precise alignment. Snap-to-grid can be toggled on/off, and grid density (columns × rows) is adjustable via input boxes.
- **Zoom Slider**: Scale the image up to 5× directly in the GUI for close-up annotation; slider remains visible at all times.
- **Color Picker**: Choose bounding-box outline color for better visibility against varied backgrounds.
- **Annotation Output**: Saves annotations to `annotations.txt` in the format:
  ```
  path/to/image.png x1,y1,x2,y2,label x1,y1,x2,y2,label...
  ```
- **Safe Update**: Editing boxes auto-updates the annotation file; deleting all boxes removes the line.
- **No Dependencies on Face Models**: Works on any image, whether or not a face is present.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fast-non-face-image-labeling-tool.git
   cd fast-non-face-image-labeling-tool
   ```
2. Install required packages:
   - `ttkbootstrap`
   - `Pillow`

## Usage

```bash
python label_tool.py
```

1. **Load Folder**: Click `Load Folder` and select your image directory.
2. **Grid Settings**: Adjust `Cols×Rows` in the grid entry boxes and press Enter to redraw.
3. **Toggle Grid**: Enable or disable grid snapping with `Disable Grid` / `Enable Grid`.
4. **Draw Boxes**:
   - Drag left mouse to draw; Press `Square mode` for 1:1 aspect ratio.
   - Right-click inside a box to remove it.
5. **Zoom**: Move the slider at bottom to zoom in/out.(There is a bug, being fixed now)
6. **Label**: Enter numeric label in the box next to `Color` before drawing.
7. **Next / Prev**: Save and proceed to next image, or just skip with `Next (No Save)`.

Annotations are stored in `annotations.txt` alongside image paths.
