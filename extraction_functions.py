import re

from verify import is_valid_aadhaar


def extract_pan_details(text) -> dict[str, str | None]:
    # Remove unwanted characters and Hindi text
    clean_text = re.sub(r"[^a-zA-Z0-9\s:/]", "", text)

    clean_text = clean_text.lower()

    # Regex pattern to extract DOB
    dob_pattern = r"\d{2}/\d{2}/\d{4}"
    dob_match = re.search(dob_pattern, clean_text)
    dob = dob_match.group() if dob_match else None

    # Extract PAN number
    pan_number = "Unknown"
    if "permanent account number" in clean_text:
        # Split the text after 'Permanent Account Number'
        after_ac_text = clean_text.split("permanent account number")[-1].strip()

        # If 'Card' exists, take the next word after 'Card' as the PAN number
        if "card" in after_ac_text:
            pan_number = after_ac_text.split("card")[1].strip().split(" ")[0]
        else:
            # Otherwise, take the next word after 'Permanent Account Number'
            pan_number = after_ac_text.split(" ")[0].strip()

    # Extract Name (3 words after 'Name')
    name = "Unknown"
    if "name" in clean_text:
        # Find the location of 'Name' in the clean text
        name_split = clean_text.split("name")
        if len(name_split) > 1:
            # Take the next 3 words after 'Name'
            name_section = name_split[1].strip().split()
            name = " ".join(name_section[:3])  # Combine the next 3 words
    else:
        name = "Unknown"

    return {"Name": name.upper(), "DOB": dob, "PAN Number": pan_number.upper()}


def extract_aadhar_details(text) -> dict[str, str | None]:
    # Remove unwanted characters and Hindi text
    clean_text = re.sub(r"[^a-zA-Z0-9\s:/]", "", text)

    # Regex pattern to extract DOB
    dob_pattern = r"\d{2}/\d{2}/\d{4}"
    dob_match = re.search(dob_pattern, clean_text)
    dob = dob_match.group() if dob_match else None

    # Regex pattern to extract Aadhaar number
    aadhar_pattern = r"\d{4}\s\d{4}\s\d{4}"
    aadhar_match = re.search(aadhar_pattern, clean_text)
    aadhar_number = aadhar_match.group() if aadhar_match else None
    isValid = False
    if aadhar_number:
        aadhar_number = aadhar_number.replace(" ", "")
        isValid = is_valid_aadhaar(aadhar_number)

    if not isValid:
        return {
            "Name": None,
            "DOB": None,
            "Gender": None,
            "Aadhar Number": None,
            "Class": "Fake",
            "Confidence": 0,
        }

    # Extract gender (Male or Female based on a keyword match)
    gender = None
    if "male" in clean_text.lower():
        gender = "Male"
    elif "female" in clean_text.lower():
        gender = "Female"

    # Extract the name
    name = None
    # Check if 'Government of India' exists
    if "Government of India" in clean_text:
        # Split the text after 'Government of India'
        after_govt_text = clean_text.split("Government of India")[-1].strip()

        # If 'Father' exists, extract the name before 'Father'
        if "Father" in after_govt_text:
            name_section = after_govt_text.split("Father")[0].strip()
        elif dob_match:
            # If 'Father' doesn't exist, extract the name before 'DOB'
            name_section = after_govt_text.split("DOB")[0].strip()
        else:
            name_section = after_govt_text

        # Clean up the name by removing digits and extra spaces
        name = re.sub(r"\d", "", name_section).strip()

    # Return the extracted information
    return {"Name": name, "DOB": dob, "Gender": gender, "Aadhar Number": aadhar_number}


def extract_passport_details(text) -> dict[str, str | None]:
    return {}


def extract_dl_details(text) -> dict[str, str | None]:
    return {}
