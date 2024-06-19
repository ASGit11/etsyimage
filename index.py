import streamlit as st
from PIL import Image, ImageOps
import zipfile
import os
import time
import shutil

def resize_and_crop(image, target_size):
    target_ratio = target_size[0] / target_size[1]
    original_ratio = image.width / image.height

    if target_ratio > original_ratio:
        new_width = target_size[0]
        new_height = round(new_width / original_ratio)
    else:
        new_height = target_size[1]
        new_width = round(new_height * original_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - target_size[0]) / 2
    top = (new_height - target_size[1]) / 2
    right = left + target_size[0]
    bottom = top + target_size[1]

    image = image.crop((left, top, right, bottom))
    return image

def resize_and_zip_images(images, sizes, output_directory, zip_filename, dpi):
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory)
    os.makedirs(output_directory, exist_ok=True)

    for uploaded_file in images:
        original_image = Image.open(uploaded_file)
        original_filename = os.path.splitext(uploaded_file.name)[0]

        for size_name, size in sizes.items():
            pixel_size = (int(size[0] * dpi), int(size[1] * dpi))
            resized_image = resize_and_crop(original_image, pixel_size)

            if resized_image.mode != 'RGB':
                resized_image = resized_image.convert('RGB')

            export_name_map = {
                '20x30': 'Ratio23',
                '18x24': 'Ratio34',
                '20x25': 'Ratio45',
                '11x14': '11x14',
                'A3': 'ISO'
            }

            size_folder = os.path.join(output_directory, size_name)
            os.makedirs(size_folder, exist_ok=True)
            output_path = os.path.join(size_folder, f'{original_filename}_{export_name_map[size_name]}.jpg')
            resized_image.save(output_path, dpi=(dpi, dpi))

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(output_directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_directory))

    return zip_filename

st.title('Image Resizer and Zipper')

uploaded_files = st.file_uploader('Upload images', type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
if uploaded_files:
    sizes = {
        '20x30': (20, 30),
        '18x24': (18, 24),
        '20x25': (20, 25),
        '11x14': (11, 14),
        'A3': (11.7, 16.5)
    }

    dpi = 300
    timestamp = int(time.time())
    zip_filename = f'resized_images_{timestamp}.zip'

    output_directory = 'output_images'
    zip_filepath = resize_and_zip_images(uploaded_files, sizes, output_directory, zip_filename, dpi)

    with open(zip_filepath, 'rb') as f:
        st.download_button('Download Resized Images', f, file_name=zip_filename)
