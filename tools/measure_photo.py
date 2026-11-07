import argparse
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk
from core.mapping import check_card_corners, measure_garment
from core.specs import load_spec

MAX_W, MAX_H = 1100, 750  # largest size the photo is shown at on screen

CARD_STEPS = [
    ("card_top_left", "Card corner 1 of 4: TOP-LEFT (the long edge is the top)"),
    ("card_top_right", "Card corner 2 of 4: TOP-RIGHT"),
    ("card_bottom_right", "Card corner 3 of 4: BOTTOM-RIGHT"),
    ("card_bottom_left", "Card corner 4 of 4: BOTTOM-LEFT"),
]


def build_steps(spec):
    """The ordered list of (name, instruction): card corners, then garment points."""
    return CARD_STEPS + [(p["name"], p["instruction"]) for p in spec["points"]]


def split_clicks(steps, clicks):
    """Separate the card corners from the garment points."""
    card_corners = clicks[:4]
    points = {name: xy for (name, _), xy in zip(steps[4:], clicks[4:])}
    return card_corners, points


def print_results(rows):
    for row in rows:
        line = f"{row['name']:<16} flat {row['flat_cm']:>6.1f} cm"
        if "garment_circumference_cm" in row:
            line += f"   round {row['garment_circumference_cm']:>6.1f} cm"
        if "estimated_body_cm" in row:
            line += f"   body (estimate) {row['estimated_body_cm']:>6.1f} cm"
        print(line)


def save_debug_image(photo_path, spec, steps, clicks, rows, out_path):
    """Save a copy of the photo showing every clicked point and each measured line."""
    image = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
    draw = ImageDraw.Draw(image)
    size = max(image.width // 150, 4)  # marker size that scales with the photo
    font = ImageFont.load_default(size=size * 3)
    points = {name: xy for (name, _), xy in zip(steps, clicks)}
    flat = {row["name"]: row["flat_cm"] for row in rows}

    for m in spec["measurements"]:
        a, b = points[m["from"]], points[m["to"]]
        draw.line([a, b], fill=(255, 200, 0), width=max(size // 2, 2))
        middle = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        draw.text(middle, f"{m['name']} {flat[m['name']]} cm", fill=(255, 255, 0), font=font)

    for name, (x, y) in points.items():
        color = (255, 0, 0) if name.startswith("card_") else (0, 120, 255)
        draw.ellipse([x - size, y - size, x + size, y + size],
                     outline=color, width=max(size // 2, 2))
        draw.text((x + size * 1.5, y - size * 2), name, fill=color, font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path)


def collect_clicks(photo_path, steps):
    """Show the photo and return the clicked points in ORIGINAL photo pixels."""
    image = ImageOps.exif_transpose(Image.open(photo_path))  # honour phone rotation
    scale = min(MAX_W / image.width, MAX_H / image.height, 1.0)
    shown = image.resize((int(image.width * scale), int(image.height * scale)))

    root = tk.Tk()
    root.title("ClothMate - click the points")
    tk_image = ImageTk.PhotoImage(shown)  # keep this variable: Tk forgets the image otherwise
    label = tk.Label(root, text="", font=("Segoe UI", 12), anchor="w")
    label.pack(fill="x")
    canvas = tk.Canvas(root, width=shown.width, height=shown.height, cursor="crosshair")
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.pack()

    clicks = []        # original-photo coordinates
    drawings = []      # canvas items drawn for each click, so Backspace can remove them

    def show_step():
        label.config(text=f"Step {len(clicks) + 1} of {len(steps)}: {steps[len(clicks)][1]}")

    def on_click(event):
        if len(clicks) >= len(steps):
            return
        clicks.append((event.x / scale, event.y / scale))  # screen -> original pixels
        name = steps[len(clicks) - 1][0]
        r = 5
        circle = canvas.create_oval(event.x - r, event.y - r, event.x + r, event.y + r,
                                    outline="red", width=2)
        text = canvas.create_text(event.x + 8, event.y - 8, text=name, anchor="w", fill="red")
        drawings.append((circle, text))
        if len(clicks) == len(steps):
            root.destroy()
        else:
            show_step()

    def on_undo(_event):
        if clicks:
            clicks.pop()
            for item in drawings.pop():
                canvas.delete(item)
            show_step()

    canvas.bind("<Button-1>", on_click)
    root.bind("<BackSpace>", on_undo)
    show_step()
    root.mainloop()
    return clicks


def main():
    parser = argparse.ArgumentParser(description="Measure a garment in a photo.")
    parser.add_argument("photo")
    parser.add_argument("spec")
    parser.add_argument("--fit", default="regular", choices=["slim", "regular", "loose"])
    args = parser.parse_args()

    spec = load_spec(args.spec)
    steps = build_steps(spec)
    clicks = collect_clicks(args.photo, steps)
    if len(clicks) < len(steps):
        print("Cancelled: not all points were clicked.")
        return

    card_corners, points = split_clicks(steps, clicks)
    try:
        ratio = check_card_corners(card_corners)
        print(f"Card shape check: long/short ratio {ratio:.2f} (a real card is 1.59)")
        rows = measure_garment(spec, card_corners, points, fit=args.fit)
    except ValueError as err:
        print(f"Cannot measure: {err}")
        return
    print_results(rows)

    out_path = Path("dataset/debug") / (Path(args.photo).stem + "_debug.jpg")
    save_debug_image(args.photo, spec, steps, clicks, rows, out_path)
    print(f"Saved a picture of your clicks to {out_path}")

if __name__ == "__main__":
    main()