from PIL import Image
import os

input_dir = "images"
output_dir = "images_converted"
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    if file.endswith((".png", ".jpg", ".jpeg", ".webp")):
        img = Image.open(os.path.join(input_dir, file)).convert("RGBA")
        img.save(os.path.join(output_dir, os.path.splitext(file)[0] + ".png"))

print("✅ All images converted to standard PNG format")
