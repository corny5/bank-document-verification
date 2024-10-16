import tensorflow as tf
from tensorflow.keras.models import load_model  # type: ignore
import numpy as np
import easyocr
from PIL import Image
import pytesseract
from extraction_functions import (
    extract_aadhar_details,
    extract_dl_details,
    extract_passport_details,
    extract_pan_details,
)

# Configuration
IMG_SIZE = (224, 224)

# Load the saved model
model = load_model("./audit_model.h5")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def predict_image(image_path) -> dict[str, float | str]:
    class_labels = [
        "aadhaar",
        "driving_license",
        "pan",
        "passport",
        "utility",
        "voter_id",
    ]
    try:
        img = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
        img_array = tf.keras.utils.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Create a batch
        img_array /= 255.0  # Rescale the image to [0, 1]

        prediction = model.predict(img_array)
        predicted_class = class_labels[np.argmax(prediction)]
        confidence = np.max(prediction)

        # print(f"Prediction: {prediction}")
        print(f"Predicted class: {predicted_class}")
        print(f"Confidence: {confidence:.2f}")
        return (
            {"class": predicted_class, "confidence": confidence}
            if confidence > 0.9
            else {
                "class": "unknown",
            }
        )

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def extract_text(image_path) -> str:
    # Initialize EasyOCR reader
    reader = easyocr.Reader(["en", "hi"])

    # Read text from the image
    result = reader.readtext(image_path)

    # Concatenate all the text found in the image
    extracted_text = " ".join([res[1] for res in result])

    return extracted_text

    # Initialize pytesseract
    # # Open an image file
    # image = Image.open(image_path)

    # # Use pytesseract to do OCR on the image
    # text = pytesseract.image_to_string(image, lang="hin+eng", config="--psm 6")

    # return text


def process_image(image_path) -> dict[str, str | None]:
    # Predict the type of document (Aadhar, PAN, etc.)
    result = predict_image(image_path)  # Example output: 'Aadhar', 'PAN', etc.
    extracted_data = {}

    # Define a dictionary mapping the predicted document type to the extraction functions
    extraction_functions = {
        "aadhaar": extract_aadhar_details,
        "pan": extract_pan_details,
        "passport": extract_passport_details,
        "driving license": extract_dl_details,
    }

    if result["class"] == "unknown":
        extracted_data["Class"] = "Unknown"
        extracted_data["Confidence"] = 0

    # Check if the prediction result has a corresponding function
    elif result["class"] in extraction_functions:
        # Extract text from the image using OCR
        text = extract_text(image_path)
        # Call the appropriate function dynamically
        extracted_data = extraction_functions[result["class"]](text)
        extracted_data["Class"] = result["class"]
        extracted_data["Confidence"] = result["confidence"]

    else:
        pass

    return extracted_data


def main():
    image_path = "./data/aadhar.jpg"
    result = process_image(image_path=image_path)
    print(result)


if __name__ == "__main__":
    main()
