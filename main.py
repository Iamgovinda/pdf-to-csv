import pytesseract
from pdf2image import convert_from_path
import os
from multiprocessing import Pool


def ocr_page(image_path):
    """Perform OCR on a single image file."""
    text = pytesseract.image_to_string(image_path, lang='eng')
    return text


def extract_text_with_ocr(pdf_path, output_dir="output_images", batch_size=10, lang='eng'):
    """
    Extracts text from an image-based PDF using OCR, processing in batches.

    Args:
        pdf_path (str): The path to the PDF file.
        output_dir (str): Directory to store converted images temporarily.
        batch_size (int): Number of pages to process at a time.
        lang (str): Language to use for OCR.

    Returns:
        str: The extracted text from the PDF.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert PDF to images
    images = convert_from_path(pdf_path, fmt='png', output_folder=output_dir)

    full_text = []

    # Process images in batches
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        image_paths = []

        # Save images temporarily
        for j, image in enumerate(batch):
            image_path = os.path.join(output_dir, f"{pdf_path.split('.')[0]}-page_{i + j + 1}.png")
            image.save(image_path, "PNG")
            image_paths.append(image_path)

        # Use multiprocessing to speed up OCR
        with Pool() as pool:
            texts = pool.map(ocr_page, image_paths)

        full_text.extend(texts)

    return "\n".join(full_text)


if __name__ == "__main__":
    # # Example usage
    pdf_path = 'C3_LE_lexique_alphabetique.pdf'
    extracted_text = extract_text_with_ocr(pdf_path)
    # image_path = "output_images/95d62c20-2f42-453c-80c1-12a7a1969fee-001.png"
    # text = ocr_page(image_path)
    # with open("output.txt", "w") as f:
    #     f.write(text)
