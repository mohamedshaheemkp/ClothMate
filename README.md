# ClothMate 👕📏

A small Streamlit app that measures a flat-laid garment from a photo, using a bank card as a ruler, and lets you ask a rule-based chatbot about the results.

Deployed in Streamlit 
Link;
https://clothmate-byshaheem.streamlit.app/

## What it does

1. **Upload a photo** of a garment laid flat, taken from straight above, with a bank card next to it on the same surface.
2. **Click 12 points** on the photo, guided step by step:
   - the 4 corners of the card (sets the scale)
   - chest: left and right armpit
   - length: shoulder-neck point, then the hem directly below
   - shoulder: left and right outer shoulder point
   - waist: left and right edge of the body
3. **See the results** in cm: chest, waist, length, shoulder, plus an estimated circumference (2 × flat width) for chest and waist.
4. **Ask the chatbot**, for example "what is the chest size?" or "how long is it?".
5. **Save garments** to a list and download them as `wardrobe.csv`.

## How it works

A photo only contains pixels, so the card (8.56 × 5.40 cm) provides the scale:

```
distance_px   = sqrt((x2 - x1)^2 + (y2 - y1)^2)
scale_w       = card_width_px  / 8.56
scale_h       = card_height_px / 5.40
dots_per_cm   = (scale_w + scale_h) / 2
measurement   = distance_px / dots_per_cm
```

Two scales are calculated as a cross-check: if they agree, the card clicks were probably accurate. The chatbot is **rule-based** (keyword matching), not machine learning.

## How to run

```bash
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Developed on Python 3.14. The app opens at http://localhost:8501.

## Accuracy test (blue polo, tape measure vs. app)

Measured by laying the shirt flat and using a tape measure, then comparing with three separate click attempts on the same photo.

| Measurement | Tape | Attempt 1 | Attempt 2 | Attempt 3 |
|---|---|---|---|---|
| Chest width | 53.0 cm | 53.8 | 51.3 | 53.4 |
| Length | 72.0 cm | 77.6 | 74.5 | 71.7 |
| Shoulder | 48.0 cm | 46.6 | 45.0 | 45.8 |
| Waist / hem* | 52.0 cm | 52.8 | 50.6 | 53.0 |

\*The tape value is the bottom hem, while the app measures the waist partway up the body, so this row is only an approximate comparison.

**Findings**
- Best attempt: chest within 0.4 cm and length within 0.3 cm of the tape; shoulder about 2 cm short.
- The same photo gave results that varied by up to 5.6 cm in length, depending on where the points were clicked. Click placement is the main source of error, not the maths.
- Length improved once the top point was defined as the shoulder-neck point instead of the top of the collar.
- Only one garment was measured with a tape, so these results are a small test, not a full evaluation.

## Limitations

- **Manual clicks:** accuracy depends on where the user clicks. The card is only about 60 pixels wide in the photo, so a few pixels of error matter.
- **Camera angle:** the photo must be taken from straight above. A tilt distorts the scale across the garment.
- **Same surface:** the card must lie on the same flat surface as the garment, or its scale will be off.
- **Wrinkles:** a straight line between two points is shorter than a tape that follows a creased fabric.
- **Circumference:** 2 × flat width is only an estimate of the real body measurement.
- **Automatic detection tried and dropped:** a simple threshold separated the shirt cleanly in 1 of 4 test photos, and failed on the light shirts because of shadows and the beige floor. Manual clicking was chosen for reliability.
- **Chatbot:** it only understands the keywords chest, length, shoulder and waist.
- **Wardrobe list:** it is held in the browser session, so download the CSV before closing the page.

## Possible next steps

- Draw the clicked points on the photo, and add an Undo button
- Offer an A4 sheet as a larger reference object
- Detect the card and garment automatically with OpenCV, as a suggestion the user can correct
- Correct for camera tilt

## Files

```
app.py               the Streamlit app
requirements.txt     dependencies
Dataset/             test photos
practice/            early practice scripts (distance and calibration)
```

## Tech

Python, [Streamlit](https://streamlit.io/), [Pillow](https://python-pillow.org/), [streamlit-image-coordinates](https://github.com/blackary/streamlit-image-coordinates)