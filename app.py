import streamlit as st
API_KEY = st.secrets["K81308556488957"]
import streamlit as st
import requests
from PIL import Image
import io

API_KEY = "K81308556488957"

def ocr_space_api(image_bytes):
    url = "https://api.ocr.space/parse/image"
    payload = {'apikey': API_KEY, 'language': 'eng', 'isOverlayRequired': False}
    files = {'file': ('image.jpg', image_bytes)}
    response = requests.post(url, data=payload, files=files)
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        return "", result.get("ErrorMessage", ["Unknown error"])[0]
    parsed_results = result.get("ParsedResults")
    if parsed_results and len(parsed_results) > 0:
        return parsed_results[0].get("ParsedText", ""), None
    else:
        return "", "No text found"

def analyze_label_text(text: str):
    feedback = []
    lower_text = text.lower()

    if "vegetarian" in lower_text:
        veg_status = "🥦 Vegetarian"
    elif "non-vegetarian" in lower_text or "non vegetarian" in lower_text:
        veg_status = "🍖 Non-Vegetarian"
    else:
        veg_status = "⚠️ Vegetarian/Non-Vegetarian declaration missing"
        feedback.append(veg_status)

    if not any(word in lower_text for word in ["ingredients", "contains"]):
        feedback.append("❌ Missing list of ingredients.")

    if not any(word in lower_text for word in ["energy", "protein", "carbohydrate", "fat"]):
        feedback.append("❌ Nutritional information missing or incomplete.")

    if "fssai" not in lower_text:
        feedback.append("❌ FSSAI logo or license number missing.")

    if not any(word in lower_text for word in ["manufactured on", "best before", "expiry", "use by"]):
        feedback.append("❌ Date marking (manufacturing/expiry) missing.")

    if not any(word in lower_text for word in ["batch no", "lot no"]):
        feedback.append("❌ Batch or lot number missing.")

    if not any(word in lower_text for word in ["net wt", "net quantity", "net weight"]):
        feedback.append("❌ Net quantity declaration missing.")

    if not feedback:
        feedback.append("✅ All mandatory FSSAI label requirements seem to be present.")

    return feedback, veg_status

st.set_page_config(page_title="FSSAI Packaging Label Checker", layout="wide")

st.title("📦 FSSAI Packaging Label OCR & Compliance Checker")

st.markdown(
    """
    Upload a clear image of the packaged food label to extract text and check compliance with FSSAI labeling guidelines.
    """
)

uploaded_file = st.file_uploader("Upload packaging label image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Performing OCR..."):
        text, error = ocr_space_api(image_bytes)

    if error:
        st.error(f"OCR Error: {error}")
    elif text.strip() == "":
        st.warning("No text detected in the image. Try a clearer image.")
    else:
        feedback, veg_status = analyze_label_text(text)

        # Layout with columns for extracted text and compliance feedback
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📄 Extracted Text")
            with st.expander("Show/Hide Raw OCR Text", expanded=True):
                st.text_area("OCR Output", text, height=400)

        with col2:
            st.subheader("🟢 Vegetarian / Non-Vegetarian Status")
            st.markdown(f"### {veg_status}")

            st.subheader("📋 Compliance Feedback")
            for item in feedback:
                st.markdown(f"- {item}")

else:
    st.info("📤 Please upload an image to begin.")

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and OCR.space API")
