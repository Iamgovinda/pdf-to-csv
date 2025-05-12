import os
from pdf2image import convert_from_path
from img2table.ocr import TesseractOCR
from img2table.document import Image

# Set paths
PDF_PATH = "C1_le_lexique_alphabetique.pdf"  # Replace with your actual PDF file path
OUTPUT_DIR = "output_images"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Convert PDF to images
images = convert_from_path(PDF_PATH)
image_paths = []

for i, img in enumerate(images):
    image_path = os.path.join(OUTPUT_DIR, f"page_{i + 1}.png")
    img.save(image_path, "PNG")
    image_paths.append(image_path)

# Initialize OCR
ocr = TesseractOCR(n_threads=1, lang="eng")

# Process each extracted image
for img_path in image_paths:
    # Load image as document
    doc = Image(img_path)

    # Extract tables
    extracted_tables = doc.extract_tables(
        ocr=ocr,
        implicit_rows=False,
        implicit_columns=False,
        borderless_tables=False,
        min_confidence=50
    )

    # Convert extracted tables to HTML
    for table_idx, table in enumerate(extracted_tables):
        html_table = "<table border='1'>\n"

        for row in table.content:
            html_table += "  <tr>\n"
            for row in table.content:
                if not isinstance(row, list):  # Check if row is actually a list
                    row = [row]  # Convert single values to a list
                for cell in row:
                    html_table += f"    <td>{cell}</td>\n"
            html_table += "  </tr>\n"

        html_table += "</table>\n"

        # Save to HTML file
        html_file = f"output_table_{table_idx + 1}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_table)

        print(f"Table {table_idx + 1} saved to {html_file}")
