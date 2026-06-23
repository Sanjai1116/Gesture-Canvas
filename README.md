# 🎨 Gesture Canvas

A real-time, hand-gesture controlled drawing application built with **OpenCV** and **MediaPipe**. Draw in the air using just your webcam — no mouse, no touchscreen, just your hand.

---

## ✨ Features

- **Air drawing** — draw freely using your index finger, tracked live via your webcam
- **Gesture-based controls** — no keyboard needed for the core drawing actions:
  - Pinch **thumb + index finger** → Erase
  - Pinch **index + middle finger** → Move / Pause (lift the "pen" without drawing)
  - No pinch → Draw normally
- **Smoothing filter** to reduce jitter and produce clean, stable lines
- **Adjustable brush size** and **5 color presets**
- **Adjustable eraser size** with a live size preview (red circle) while erasing
- **4 background modes** — live camera feed, white, black, or blue
- **Hand skeleton overlay** for visual feedback on any background
- **Save your drawing** as a PNG image
- **Record your session** as an MP4 video, with an on-screen REC indicator

---

## 🖥️ Demo

| Mode | Gesture |
|------|---------|
| Draw | Default hand position (no pinch) |
| Erase | Pinch thumb + index finger together |
| Move / Pause | Pinch index + middle finger together |

---

## 📦 Requirements

- Python 3.9 – 3.12 recommended
- A working webcam

Dependencies are listed in [`requirements.txt`](requirements.txt):

```
opencv-python
mediapipe
numpy
```

---

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/gesture-canvas.git
   cd gesture-canvas
   ```

2. (Optional but recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python gesture_canvas.py
   ```

---

## 🎮 Controls

### Hand Gestures
| Gesture | Action |
|---|---|
| Default (no pinch) | Draw with index finger |
| Thumb + Index pinch | Erase (spot eraser) |
| Index + Middle pinch | Move / Pause (no drawing) |

### Keyboard Shortcuts
| Key | Action |
|---|---|
| `1`–`5` | Change brush color (Yellow, Cyan, Green, Red, White) |
| `+` / `-` | Increase / decrease brush size |
| `↑` (Up Arrow) | Increase eraser size |
| `↓` (Down Arrow) | Decrease eraser size |
| `B` | Cycle background (Camera → White → Black → Blue) |
| `C` | Clear the canvas |
| `S` | Save the current canvas as a PNG image |
| `V` | Start / stop screen recording (saved as MP4) |
| `Q` | Quit the application |

---

## ⚙️ How It Works

1. **MediaPipe Hands** detects 21 hand landmarks per frame from the webcam feed.
2. The **index fingertip** position is used as the drawing cursor and smoothed using an exponential moving average to reduce jitter.
3. **Euclidean distance** between the thumb tip and other fingertips is used to detect pinch gestures (no finger-bend detection is needed — distance-based detection works for any hand orientation).
4. Drawing is rendered onto a transparent canvas layer, which is then composited on top of the selected background (live camera, white, black, or blue) on every frame.

---

## 🛠️ Tech Stack

- [OpenCV](https://opencv.org/) — video capture, image processing, and rendering
- [MediaPipe](https://developers.google.com/mediapipe) — real-time hand landmark detection
- [NumPy](https://numpy.org/) — array and image buffer operations

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and distribute it.

---

## 🙌 Acknowledgements

Built using Google's [MediaPipe](https://developers.google.com/mediapipe) hand tracking solution.
