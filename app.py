import math
import streamlit as st
from PIL import Image , ImageOps
from streamlit_image_coordinates import streamlit_image_coordinates

def distance(x1, y1, x2, y2):
    result = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
    return result

def to_cm(dots, dots_per_cm):
    return round(dots / dots_per_cm , 1)

def reply(question, results):
    q = question.lower()
    if "chest" in q:
        return f"Your chest is {results['chest']} cm flat, about {round(results['chest'] * 2, 1)} cm around."
    
    elif "length" in q:
        return f"Your length is {results['length']} cm."
        
    elif "shoulder" in q:
        return f"Your shoulder width is {results['shoulder']} cm."
    
    elif "waist" in q:
        return f"Your waist is {results['waist']} cm."
        
    else:
        return "Try asking about the chest, length, shoulder, or waist."


st.set_page_config(layout="wide")
st.title("ClothMate")

photo = st.file_uploader("Upload a photo of your clothes", type=["jpg", "jpeg", "png"])

if photo is None:
    st.write("Please upload a photo.")
else:
    img = Image.open(photo)
    img = ImageOps.exif_transpose(img)
    new_height = int(800 * img.height / img.width)
    img = img.resize((800, new_height))

    if "points" not in st.session_state:
        st.session_state.points = []
        st.session_state.last_time = 0

    if "chat" not in st.session_state:
        st.session_state.chat = []

    if "wardrobe" not in st.session_state:
        st.session_state.wardrobe = []

        
    steps = ["Card: top-left corner", "Card: top-right corner",
         "Card: bottom-left corner", "Card: bottom-right corner",
         "Chest: left armpit", "Chest: right armpit",
         "Length: top (collar base)", "Length: bottom (hem)",
         "Shoulder: left end", "Shoulder: right end",
         "Waist: left edge", "Waist: right edge"]

    left, right = st.columns([3, 2])

    with left:
        if st.button("Start over"):
            st.session_state.points = []
            st.session_state.chat = []

        click = streamlit_image_coordinates(img)
        if click is not None and click["unix_time"] != st.session_state.last_time and len(st.session_state.points) < len(steps):
            st.session_state.last_time = click["unix_time"]
            st.session_state.points.append((click["x"], click["y"]))

    with right:
        n = len(st.session_state.points)

        if n < len(steps):
            st.write("Next click:", steps[n])
        else:
            st.write("All points collected!")
            p = st.session_state.points


            x1, y1 = p[0]
            x2, y2 = p[1]
            card_w_px = distance(x1, y1, x2, y2)

            x1, y1 = p[0]
            x2, y2 = p[2]
            card_h_px = distance(x1, y1, x2, y2)

            scale_w = card_w_px / 8.56
            scale_h = card_h_px / 5.4

            dots_per_cm = (scale_w + scale_h) / 2

            chest_px = distance(p[4][0], p[4][1], p[5][0], p[5][1])
            chest_cm = to_cm(chest_px, dots_per_cm)

            length_px = distance(p[6][0], p[6][1], p[7][0], p[7][1])
            length_cm = to_cm(length_px, dots_per_cm)

            shoulder_px = distance(p[8][0], p[8][1], p[9][0], p[9][1])
            shoulder_cm = to_cm(shoulder_px, dots_per_cm)

            waist_px = distance(p[10][0], p[10][1], p[11][0], p[11][1])
            waist_cm = to_cm(waist_px, dots_per_cm)

            st.write("Chest width (flat):", chest_cm, "cm")
            st.write("Chest circumference (estimate):", round(chest_cm * 2, 1), "cm")
            st.write("Length:", length_cm, "cm")
            st.write("Shoulder width:", shoulder_cm, "cm")
            st.write("Waist width (flat):", waist_cm, "cm")
            st.write("Waist circumference (estimate):", round(waist_cm * 2, 1), "cm")

            results = {"chest": chest_cm, "length": length_cm, "shoulder": shoulder_cm, "waist": waist_cm}
            name = st.text_input("Name this garment", "Blue polo")

            if st.button("Save garment"):
                row = {"name": name, "chest": chest_cm, "length": length_cm, "shoulder": shoulder_cm, "waist": waist_cm}
                st.session_state.wardrobe.append(row)
                st.success("Saved!")

            question = st.chat_input("Ask about your garment...")
            if len(st.session_state.wardrobe) > 0:
                st.write("Saved garments")
                st.table(st.session_state.wardrobe)

                csv_text = "name,chest,length,shoulder,waist\n"
                for row in st.session_state.wardrobe:
                    csv_text += f"{row['name']},{row['chest']},{row['length']},{row['shoulder']},{row['waist']}\n"

                st.download_button("Download wardrobe CSV", csv_text, "wardrobe.csv", "text/csv")
            if question:
                answer = reply(question, results)
                st.session_state.chat.append(("user", question))
                st.session_state.chat.append(("assistant", answer))

            for role, text in st.session_state.chat:
                st.chat_message(role).write(text)
            