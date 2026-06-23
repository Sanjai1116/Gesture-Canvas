import cv2
import mediapipe as mp
import numpy as np
import time

# ─── MediaPipe Setup ──────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

# ─── Color Palette ────────────────────────────────────────────
color_list = [
    ("Yellow", (0, 255, 255)),
    ("Cyan",   (255, 255, 0)),
    ("Green",  (0, 255, 0)),
    ("Red",    (0, 0, 255)),
    ("White",  (255, 255, 255)),
]

# ─── Background Modes ─────────────────────────────────────────
BG_NAMES  = ["Camera", "White", "Black", "Blue"]
BG_COLORS = [None, (255, 255, 255), (0, 0, 0), (200, 80, 20)]

# ─── State ────────────────────────────────────────────────────
canvas        = None
brush_color   = (0, 255, 255)
brush_size    = 8
eraser_size   = 35
bg_mode       = 0
PINCH_THRESH  = 40
SMOOTH_FACTOR = 0.5

prev_x, prev_y = 0, 0
smooth_x, smooth_y = 0, 0
was_drawing    = False
first_point    = True

recording    = False
video_writer = None
record_file  = ""

UP_ARROW   = 2490368
DOWN_ARROW = 2621440

# ─── Helpers ─────────────────────────────────────────────────

def tip_pos(lm, tip_id, w, h):
    pt = lm.landmark[tip_id]
    return int(pt.x * w), int(pt.y * h)

def draw_ui(img, mode_text, bg_name, b_size, e_size, b_color, is_rec):
    h, w = img.shape[:2]

    for i, (name, col) in enumerate(color_list):
        x1, y1 = 10 + i * 72, 10
        x2, y2 = 72 + i * 72, 62
        cv2.rectangle(img, (x1, y1), (x2, y2), col, -1)
        if col == b_color:
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        cv2.putText(img, str(i + 1), (x1 + 6, y2 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    # ── REC indicator top-right corner ──
    if is_rec:
        cv2.circle(img, (w - 110, 28), 10, (0, 0, 255), -1)
        cv2.putText(img, "REC", (w - 90, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.rectangle(img, (0, h - 44), (w, h), (25, 25, 25), -1)
    status  = (f"Mode: {mode_text}  |  BG: {bg_name}  |"
               f"  Brush: {b_size}  |  Eraser: {e_size}  |"
               f"  Keys: B=BG  C=Clear  S=Save  V=Record  Up/Down=Eraser  Q=Quit")
    cv2.putText(img, status, (10, h - 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (190, 190, 190), 1)

# ─── Webcam ───────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("=" * 52)
print("       Gesture Canvas — Started!")
print("=" * 52)
print("  Default (no pinch)        → Draw (index tip)")
print("  Thumb + Index pinch       → Erase")
print("  Index + Middle pinch      → Move / Pause")
print("  B / b                     → Cycle background")
print("  S                         → Save image (PNG)")
print("  V                         → Record / Stop + Save MP4")
print("  Up Arrow                  → Eraser size +")
print("  Down Arrow                → Eraser size -")
print("  + / -                     → Brush size +/-")
print("  1–5                       → Change color")
print("  Q                         → Quit")
print("=" * 52)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame      = cv2.flip(frame, 1)
    h, w, _    = frame.shape

    if canvas is None:
        canvas = np.zeros((h, w, 3), dtype=np.uint8)

    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    mode_text   = "IDLE"
    dist_erase  = None
    dist_move   = None
    erase_point = None   # for red dot indicator

    hand_lm_to_draw = None  # store landmarks to draw on final combined image

    if result.multi_hand_landmarks:
        for hand_lm in result.multi_hand_landmarks:
            hand_lm_to_draw = hand_lm

            ix, iy = tip_pos(hand_lm, 8,  w, h)   # index tip
            tx, ty = tip_pos(hand_lm, 4,  w, h)   # thumb tip
            mx, my = tip_pos(hand_lm, 12, w, h)   # middle tip

            if first_point:
                smooth_x, smooth_y = ix, iy
                first_point = False
            else:
                smooth_x = int(SMOOTH_FACTOR * smooth_x + (1 - SMOOTH_FACTOR) * ix)
                smooth_y = int(SMOOTH_FACTOR * smooth_y + (1 - SMOOTH_FACTOR) * iy)

            sx, sy = smooth_x, smooth_y

            dist_erase = ((ix - tx) ** 2 + (iy - ty) ** 2) ** 0.5
            dist_move  = ((ix - mx) ** 2 + (iy - my) ** 2) ** 0.5

            if dist_erase < PINCH_THRESH:
                was_drawing = False
                cv2.circle(canvas, (ix, iy), eraser_size, (0, 0, 0), -1)
                mode_text   = "ERASE"
                erase_point = (ix, iy)

            elif dist_move < PINCH_THRESH:
                was_drawing  = False
                prev_x, prev_y = sx, sy
                mode_text = "MOVE"

            else:
                if was_drawing:
                    cv2.line(canvas,
                             (prev_x, prev_y), (sx, sy),
                             brush_color, brush_size,
                             lineType=cv2.LINE_AA)
                was_drawing    = True
                prev_x, prev_y = sx, sy
                mode_text = "DRAW"
    else:
        was_drawing = False
        first_point = True

    # ─── Build background ────────────────────────────────────
    if bg_mode == 0:
        bg = frame.copy()
    else:
        bg = np.full((h, w, 3), BG_COLORS[bg_mode], dtype=np.uint8)

    gray      = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask   = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    mask_inv  = cv2.bitwise_not(mask)
    bg_part   = cv2.bitwise_and(bg,     bg,     mask=mask_inv)
    draw_part = cv2.bitwise_and(canvas, canvas, mask=mask)
    combined  = cv2.add(bg_part, draw_part)

    # ── Draw hand skeleton on top of final image (any background) ──
    if hand_lm_to_draw is not None:
        mp_draw.draw_landmarks(combined, hand_lm_to_draw, mp_hands.HAND_CONNECTIONS)

    # ── Red dot indicator showing eraser size while erasing ──
    if erase_point is not None:
        cv2.circle(combined, erase_point, eraser_size, (0, 0, 255), 2)
        cv2.circle(combined, erase_point, 4, (0, 0, 255), -1)

    draw_ui(combined, mode_text, BG_NAMES[bg_mode],
            brush_size, eraser_size, brush_color, recording)

    if recording and video_writer:
        video_writer.write(combined)

    cv2.imshow("Gesture Canvas", combined)

    # ─── Key handling ────────────────────────────────────────
    key = cv2.waitKeyEx(1)

    if key == ord('q') or key == ord('Q'):
        break

    elif key in (ord('c'), ord('C')):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        print("[Cleared] Canvas reset.")

    elif key in (ord('b'), ord('B')):
        bg_mode = (bg_mode + 1) % len(BG_NAMES)

    elif key in (ord('s'), ord('S')):
        fname = f"canvas_{int(time.time())}.png"
        cv2.imwrite(fname, combined)
        print(f"[Saved] {fname}")

    elif key in (ord('v'), ord('V')):
        if not recording:
            record_file  = f"canvas_rec_{int(time.time())}.mp4"
            fourcc       = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(record_file, fourcc, 20.0, (w, h))
            recording    = True
            print(f"[Recording] Started → {record_file}")
        else:
            recording = False
            video_writer.release()
            video_writer = None
            print(f"[Recording] Saved → {record_file}")

    elif key == ord('+') or key == ord('='):
        brush_size = min(brush_size + 2, 40)

    elif key == ord('-'):
        brush_size = max(brush_size - 2, 2)

    elif key == UP_ARROW:
        eraser_size = min(eraser_size + 5, 100)

    elif key == DOWN_ARROW:
        eraser_size = max(eraser_size - 5, 10)

    elif ord('1') <= key <= ord('5'):
        brush_color = color_list[key - ord('1')][1]

# ─── Cleanup ─────────────────────────────────────────────────
if recording and video_writer:
    video_writer.release()
    print(f"[Recording] Auto-saved → {record_file}")

cap.release()
cv2.destroyAllWindows()
print("Gesture Canvas closed.")