import streamlit as st
from PIL import Image
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def analyze_label_text(text: str):
    feedback = []
    lower_text = text.lower()

    # Vegetarian / Non-Vegetarian detection
    if "vegetarian" in lower_text:
        veg_status = "Vegetarian"
    elif "non-vegetarian" in lower_text or "non vegetarian" in lower_text:
        veg_status = "Non-Vegetarian"
    else:
        veg_status = "Vegetarian/Non-Vegetarian declaration missing"
        feedback.append(veg_status)

    # Other checks...
    if not any(word in lower_text for word in ["ingredients", "contains"]):
        feedback.append("Missing list of ingredients.")
    
    if not any(word in lower_text for word in ["energy", "protein", "carbohydrate", "fat"]):
        feedback.append("Nutritional information missing or incomplete.")

    if not ("fssai" in lower_text):
        feedback.append("FSSAI logo or license number missing.")

    if not any(word in lower_text for word in ["manufactured on", "best before", "expiry", "use by"]):
        feedback.append("Date marking (manufacturing/expiry) missing.")

    if not any(word in lower_text for word in ["batch no", "lot no"]):
        feedback.append("Batch or lot number missing.")

    if not any(word in lower_text for word in ["net wt", "net quantity", "net weight"]):
        feedback.append("Net quantity declaration missing.")

    if not feedback:
        feedback.append("All mandatory FSSAI label requirements seem to be present.")

    return feedback, veg_status

def highlight_issues(text, feedback):
    # Simple approach: highlight words related to issues
    # For demo, highlight "missing", "not", "incomplete" words red if present in text

    # We'll just highlight the keywords from feedback in the extracted text where possible

    highlighted = text
    for issue in feedback:
        # Extract key phrase from feedback for highlight, e.g. "missing list of ingredients" => "ingredients"
        words = re.findall(r'\b\w+\b', issue)
        keywords = [w for w in words if w.lower() not in ("missing", "not", "in", "or", "declaration", "information", "declarations", "declaration", "declaration", "mandatory")]
        for kw in keywords:
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            highlighted = pattern.sub(f'**:red[{kw}]**', highlighted)

    return highlighted

st.title("FSSAI Packaging Label OCR & Compliance Checker")

uploaded_file = st.file_uploader("Upload a packaging image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    text = pytesseract.image_to_string(image)
    st.subheader("Extracted Text")

    feedback, veg_status = analyze_label_text(text)

    highlighted_text = highlight_issues(text, feedback)
    st.markdown(highlighted_text)

    st.subheader("Vegetarian / Non-Vegetarian Status:")
    st.markdown(f"**{veg_status}**")

    st.subheader("Compliance Feedback")
    for item in feedback:
        st.markdown(f"- {item}")
