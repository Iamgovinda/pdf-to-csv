import pytesseract
from pdf2image import convert_from_path
import os
import csv
import re
from concurrent.futures import ThreadPoolExecutor


def ocr_page(image_path):
    """Perform OCR on a single image file."""
    print(f"Processing {image_path}")
    text = pytesseract.image_to_string(image_path, lang='eng')
    return os.path.basename(image_path), text


def extract_text_from_images(image_dir):
    """Extract text from all images in a directory using multithreading."""
    texts = []
    image_files = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir))[:1] if f.endswith(".png")]

    with ThreadPoolExecutor() as executor:
        results = executor.map(ocr_page, image_files)
        texts.extend(results)

    return texts


def clean_text(text):
    """Remove timestamps, unwanted email prefixes, numeric keys, and extra keys."""
    text = re.sub(r'\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4} \d{1,2}:\d{2} [APap][Mm]', '', text)  # Remove timestamps
    text = re.sub(r'mailto:', '', text, flags=re.IGNORECASE)  # Remove mailto:
    text = re.sub(r'http:', '', text, flags=re.IGNORECASE)  # Remove mailto:
    text = re.sub(r'https:', '', text, flags=re.IGNORECASE)  # Remove mailto:
    text = re.sub(r'^> On .*?, at .*?, .*?$', '', text, flags=re.MULTILINE)  # Remove unwanted email headers
    text = re.sub(r'^\d+:', '', text, flags=re.MULTILINE)  # Remove numeric keys (e.g., '123:')
    return text


def parse_text_to_dict(texts):
    """Parse extracted text into a structured dictionary."""
    entries = []

    for file_name, text in texts:
        text = clean_text(text)
        entry = {"file_name": file_name}

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                if key == "Full Name" and len(entry) > 1:
                    entries.append(entry)
                    entry = {"file_name": file_name}
                entry[key] = value

        if len(entry) > 1:
            entries.append(entry)

    return entries


def write_csv(filename, data):
    """Write structured data to CSV and remove columns with all null values."""
    if not data:
        print("No data to write.")
        return

    # Identify all unique keys dynamically from all entries
    all_keys = set()
    for entry in data:
        all_keys.update(entry.keys())

    # Remove columns where all values are None or empty
    filtered_keys = [key for key in all_keys if any(entry.get(key) for entry in data)]

    if "Full Name" in filtered_keys:
        filtered_keys.remove("Full Name")
        filtered_keys = ["Full Name"] + sorted(filtered_keys)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filtered_keys, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    image_dir = "output_images"
    output_text_file = "output.txt"
    output_csv_file = "final_output.csv"

    extracted_texts = extract_text_from_images(image_dir)
    with open(output_text_file, "w", encoding="utf-8") as f:
        f.write("\n".join(text for _, text in extracted_texts))
    parsed_data = parse_text_to_dict(extracted_texts)
    write_csv(output_csv_file, parsed_data)
