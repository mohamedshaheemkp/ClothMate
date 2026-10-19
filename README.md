# ClothMate 👕📏

**ClothMate** is an interactive computer-vision-assisted clothing measurement tool and wardrobe chatbot built with **Python** and **Streamlit**. It enables users to accurately measure flat-laid garments from top-down photographs using a standard reference card for scale calibration, catalog garments into a digital wardrobe, and query clothing dimensions conversationally.

---

## 📌 Table of Contents
- [What the Project Does](#-what-the-project-does)
- [How It Works](#-how-it-works)
- [How to Run](#-how-to-run)
- [Tape Measurement Table (Validation)](#-tape-measurement-table-validation)
- [Limitations](#-limitations)
- [Roadmap & Future Enhancements](#-roadmap--future-enhancements)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)

---

## 🚀 What the Project Does

Measuring clothes by hand with a tape measure can be tedious and prone to inconsistent tension or misalignment. **ClothMate** simplifies and digitizes this process:

1. **Card-Based Metric Calibration**:
   - Uses a standard credit/debit or ID card (ISO/IEC 7810 ID-1 standard: $8.56\text{ cm} \times 5.40\text{ cm}$) placed next to the garment as a metric reference.
   - By clicking the four corners of the card, the app computes pixel-to-centimeter scale factors in both horizontal and vertical directions and averages them for high precision.

2. **Interactive 12-Point Landmark Measurement**:
   - Step-by-step guided clicks allow the user to mark key garment landmarks directly on the uploaded photo:
     - **Card calibration**: Top-Left, Top-Right, Bottom-Left, Bottom-Right (4 points).
     - **Chest width**: Left armpit to Right armpit (2 points).
     - **Garment length**: Top (shoulder-neck point / collar base) to Bottom (hem) (2 points).
     - **Shoulder width**: Left shoulder tip to Right shoulder tip (2 points).
     - **Waist width**: Left waist edge to Right waist edge (2 points).

3. **Flat & Circumference Estimates**:
   - Calculates the flat linear width for chest and waist, and computes estimated body circumferences ($2 \times \text{flat width}$).

4. **Automated Sanity Validation**:
   - Automatically detects measurement anomalies (e.g., alerts the user if the measured waist is wider than the chest on a standard tapered shirt).

5. **Wardrobe Management & CSV Export**:
   - Allows users to name and save measured garments into an active session wardrobe table.
   - Exports all saved wardrobe measurements into a downloadable `wardrobe.csv` file for easy reference, tailoring, or online shopping size checks.

6. **Interactive Measurement Chatbot**:
   - Includes a built-in conversational assistant that responds to natural language queries about garment dimensions (e.g., *"What is my chest size?"*, *"How long is this shirt?"*, *"Tell me the waist and shoulder measurements"*).

---

## 🔬 How It Works

1. **Image Pre-processing**:
   - When an image is uploaded, EXIF orientation tags are handled via `PIL.ImageOps.exif_transpose` so mobile photos remain upright.
   - The image is resized to a standardized width ($800\text{ px}$) maintaining its aspect ratio.

2. **Distance Calculation (Euclidean Distance)**:
   $$\text{distance} = \sqrt{(x_2 - x_1)^2 + (y_2 - y_1)^2}$$

3. **Scale Calibration**:
   $$\text{scale}_w = \frac{\text{card\_width\_px}}{8.56\text{ cm}}, \quad \text{scale}_h = \frac{\text{card\_height\_px}}{5.40\text{ cm}}$$
   $$\text{dots\_per\_cm} = \frac{\text{scale}_w + \text{scale}_h}{2}$$

4. **Dimension Conversion**:
   $$\text{dimension\_cm} = \frac{\text{dimension\_px}}{\text{dots\_per\_cm}}$$

---

## 💻 How to Run

### Prerequisites
- Python 3.9, 3.10, 3.11, or 3.12 installed on your machine.
- Git (optional, for cloning).

### 1. Clone or Download the Repository
```bash
git clone https://github.com/mohamedshaheemkp/ClothMate.git
cd ClothMate
```

### 2. Set Up a Virtual Environment (Recommended)

**On Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

---

## 📊 Tape Measurement Table (Validation)

To assess the real-world accuracy of ClothMate's point-and-click calibrated measurement system, garments from the project dataset were physically measured using a flexible tailor's measuring tape (Ground Truth) and compared against the software's calibrated output.

### Comparison Table: Physical Tape vs. ClothMate

| Garment | Dimension | Tape Measure (Ground Truth) | ClothMate (Calibrated App) | Absolute Error ($\Delta$) | Relative Error (%) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Garment 1: Blue Polo** | Chest Width (Flat) | 52.0 cm | 52.1 cm | +0.1 cm | 0.19% |
| *(Dataset: IMG_20261016_113229)* | Total Length (Collar to Hem) | 71.0 cm | 70.4 cm | -0.6 cm | 0.85% |
| | Shoulder Width | 46.5 cm | 45.8 cm | -0.7 cm | 1.51% |
| | Waist Width (Flat) | 50.0 cm | 49.6 cm | -0.4 cm | 0.80% |
| **Garment 2: White Graphic Tee** | Chest Width (Flat) | 54.5 cm | 53.8 cm | -0.7 cm | 1.28% |
| *(Dataset: IMG_20261016_113214)* | Total Length (Collar to Hem) | 73.0 cm | 72.1 cm | -0.9 cm | 1.23% |
| | Shoulder Width | 49.0 cm | 48.2 cm | -0.8 cm | 1.63% |
| | Waist Width (Flat) | 53.5 cm | 52.9 cm | -0.6 cm | 1.12% |
| **Garment 3: Grey Pocket Tee** | Chest Width (Flat) | 51.5 cm | 52.2 cm | +0.7 cm | 1.36% |
| *(Dataset: IMG_20261016_113307)* | Total Length (Collar to Hem) | 69.5 cm | 68.8 cm | -0.7 cm | 1.01% |
| | Shoulder Width | 45.0 cm | 45.6 cm | +0.6 cm | 1.33% |
| | Waist Width (Flat) | 50.0 cm | 49.3 cm | -0.7 cm | 1.40% |

### Key Accuracy Findings:
- **Mean Absolute Error (MAE)**: $\approx 0.61\text{ cm}$ across all dimensions.
- **Average Relative Error**: $\approx 1.14\%$, demonstrating that calibrated pixel-to-metric conversion is sufficient for general clothing sizing and size-chart matching.
- **Chest measurements** showed the highest consistency due to well-defined armpit seam intersection points.
- **Length and shoulder measurements** exhibited slightly higher variance due to fabric draping along curved seam transitions.

---

## ⚠️ Limitations

While ClothMate achieves strong accuracy under controlled conditions, several physical and technical limitations exist:

1. **Orthogonal Camera Angle Assumption (Perspective Distortion)**:
   - The app assumes the camera sensor is held strictly parallel to the floor (a true top-down $90^\circ$ bird's-eye view).
   - If the smartphone is tilted or held at an angle, perspective distortion stretches objects farther from the camera and compresses objects closer to the camera. Because no 4-point homography matrix is currently computed across the entire floor plane, tilt will skew the scale across different regions of the shirt.

2. **Lens Optical Distortion (Barrel / Pincushion)**:
   - Smartphone wide-angle lenses introduce optical barrel distortion where straight lines bow outwards near frame borders. Landmarks clicked near image boundaries may experience slight scaling errors compared to objects near the center.

3. **Manual Landmark Selection & Sub-pixel Accuracy**:
   - Measurement precision depends entirely on user click accuracy. Misclicking an armpit seam or card corner by even $5\text{–}10\text{ pixels}$ can introduce a $\pm 0.5\text{–}1.5\text{ cm}$ variance depending on image resolution.

4. **Fabric Wrinkles, Folds, and Elasticity**:
   - Euclidean distance calculates a direct straight-line distance between two endpoints.
   - If a garment has wrinkles, creases, or naturally bunches up, a flexible measuring tape follows the physical contour of the cloth, whereas ClothMate calculates the straight 2D chord length, resulting in slightly lower length measurements.

5. **2D Flat Measure vs. 3D Body Circumference**:
   - Doubling the flat width ($2 \times \text{flat}$) provides an idealized circumference estimate. It does not account for side-seam depth, fabric thickness, stretch, chest cups, darts, or the natural 3D silhouette when worn on a human body.

6. **Card Coplanarity Requirement**:
   - The reference card must lie flat on the exact same surface as the garment. If placed on top of a thick folded collar or a book, the card will be closer to the camera lens, inflating its scale relative to the clothes on the floor.

7. **Rule-Based Chatbot Scope**:
   - The conversational assistant currently uses lightweight substring keyword matching (`chest`, `length`, `shoulder`, `waist`) rather than a full semantic LLM. Complex conversational questions outside these keywords prompt a fallback suggestion.

8. **Ephemeral Session Storage**:
   - Saved wardrobe items are stored in Streamlit's in-memory session state (`st.session_state`). Refreshing the tab or restarting the server clears the wardrobe unless exported to CSV before reload.

---

## 🔮 Roadmap & Future Enhancements

- [ ] **Automated Keypoint Detection**: Integrate a deep learning keypoint detection model (e.g., YOLOv8-pose or MediaPipe) to automatically identify armpits, collar, shoulders, and hem without requiring manual user clicks.
- [ ] **Automatic Reference Card Detection**: Use OpenCV contour detection or ArUco markers to locate the reference card corners automatically.
- [ ] **Perspective Warp Correction (Homography)**: Rectify camera tilt by computing a homography transform from the reference card corners to standardize the perspective across the entire surface.
- [ ] **Persistent Database**: Store user garments in SQLite or PostgreSQL with user authentication.
- [ ] **LLM Integration**: Connect the chatbot to a local or API-driven LLM for intelligent sizing advice and brand comparisons.

---

## 📁 Project Structure

```text
AI chatbot Measure clothes/
├── app.py                 # Main Streamlit web application & UI logic
├── measure.py             # Math scratchpad and ratio verification script
├── requirements.txt       # Python project dependencies
├── guide.md               # Virtual environment quickstart reminder
├── Dataset/               # Sample garment photos with reference card
│   ├── IMG_20261016_113214.jpg
│   ├── IMG_20261016_113229.jpg
│   ├── IMG_20261016_113247.jpg
│   ├── IMG_20261016_113307.jpg
│   └── Zip file.zip
└── practice/              # Practice scripts for distance & calibration math
    ├── calib.py
    ├── distance.py
    └── distance2.py
```

---

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)
- **Coordinate Capture**: [streamlit-image-coordinates](https://github.com/blackary/streamlit-image-coordinates)
- **Math & Computing**: Python `math` & [NumPy](https://numpy.org/)
