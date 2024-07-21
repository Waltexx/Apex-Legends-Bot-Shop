import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file
import os

app = Flask(__name__)
port = 5001

def fetch_images():
    url = "https://apexitemstore.com/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    section = "Corrupted Summer Store"
    section_header = soup.find('h3', string=section)
    if section_header:
        next_element = section_header.find_next()
        while next_element and next_element.name not in ['ul', 'p']:
            next_element = next_element.find_next()
        if next_element:
            return [img.get('src') for img in next_element.find_all('img') if img.get('src')]
    return []

def create_composite_image(image_urls):
    bg_path = r"C:\\Users\\AdminLocal\\Desktop\\APYY\\Background.png"
    bg_image = Image.open(bg_path)
    title_font = ImageFont.truetype("arialbd.ttf", 200)
    section_font = ImageFont.truetype("arialbd.ttf", 180)
    title_color = (255, 255, 255)
    margin, padding, scale = 50, 40, 6
    composite_width, composite_height = 12000, 10000

    bg_image = bg_image.resize((composite_width, composite_height))
    draw = ImageDraw.Draw(bg_image)
    main_title, section_title = "SHOP APEX LEGENDS", "Corrupted Summer Store"
    main_title_bbox = draw.textbbox((0, 0), main_title, font=title_font)
    draw.text(((composite_width - (main_title_bbox[2] - main_title_bbox[0])) // 2, margin), main_title, font=title_font, fill=title_color)
    current_y = margin + (main_title_bbox[3] - main_title_bbox[1]) + padding
    draw.text((margin, current_y), section_title, font=section_font, fill=title_color)
    current_y += 180 + padding

    current_x, row_height = margin, 0
    for url in image_urls:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        img = Image.open(response.raw)
        img = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
        if current_x + img.width > composite_width - margin:
            current_x, current_y = margin, current_y + row_height + padding
            row_height = 0
        bg_image.paste(img, (current_x, current_y))
        current_x += img.width + padding
        row_height = max(row_height, img.height)
    return bg_image

@app.route('/api/composite_image', methods=['GET'])
def get_composite_image():
    images = fetch_images()
    composite_image = create_composite_image(images)
    composite_image_path = os.path.join(os.getcwd(), "composite_image.jpg")
    composite_image.save(composite_image_path)
    return send_file(composite_image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, port=port)
