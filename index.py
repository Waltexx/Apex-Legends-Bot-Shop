import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

def fetch_images():
    url = "https://apexitemstore.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Cette ligne lance une exception pour les erreurs HTTP
        soup = BeautifulSoup(response.content, "html.parser")
        section = "Corrupted Summer Store"
        section_header = soup.find('h3', string=section)
        if section_header:
            next_element = section_header.find_next()
            while next_element and next_element.name not in ['ul', 'p']:
                next_element = next_element.find_next()
            if next_element:
                return [img.get('src') for img in next_element.find_all('img') if img.get('src')]
    except requests.exceptions.HTTPError as e:
        app.logger.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request exception occurred: {e}")
    except Exception as e:
        app.logger.error(f"Unexpected error occurred: {e}")
    return []

def create_composite_image(image_urls):
    try:
        bg_path = "Background.png"  # Assurez-vous que ce fichier est dans le bon répertoire
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
            try:
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
            except Exception as e:
                app.logger.error(f"Error processing image {url}: {e}")
        return bg_image
    except Exception as e:
        app.logger.error(f"Error creating composite image: {e}")
        return None

@app.route('/api/composite_image', methods=['GET'])
def get_composite_image():
    try:
        images = fetch_images()
        composite_image = create_composite_image(images)
        if composite_image:
            composite_image_path = os.path.join(os.getcwd(), "composite_image.jpg")
            composite_image.save(composite_image_path)
            return send_file(composite_image_path, mimetype='image/jpeg')
        else:
            return jsonify({"error": "Error creating composite image"}), 500
    except Exception as e:
        app.logger.error(f"Error in endpoint /api/composite_image: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
