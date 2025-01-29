import os
from PIL import Image
from pathlib import Path

input_folder = Path("images")
output_folder = Path("resized_images")
output_folder.mkdir(exist_ok=True)

def compress_image(image_path, output_path):
    try:
        with Image.open(image_path) as img:
            img.convert("RGB").save(output_path, "JPEG", quality=50)
    except Exception as e:
        print(f"Error {image_path}: {e}")

for image_file in input_folder.rglob("*.png"):
    relative_path = image_file.relative_to(input_folder)
    output_path = output_folder / relative_path.with_suffix(".jpg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    compress_image(image_file, output_path)
