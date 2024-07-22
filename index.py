# index.py

from flask import Flask, send_file, jsonify
import requests
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

def fetch_images():
    url = "https://apexitemstore.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Utiliser BeautifulSoup pour extraire les URLs des images
        from bs4 import BeautifulSoup
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
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

def create_composite_image(image_urls):
    try:
        composite_width, composite_height = 1200, 1000
        bg_image = Image.new("RGB", (composite_width, composite_height), (255, 255, 255))
        draw = ImageDraw.Draw(bg_image)
        title_font = ImageFont.load_default()
        title_color = (0, 0, 0)
        draw.text((10, 10), "Composite Image", font=title_font, fill=title_color)

        current_x, current_y = 10, 40
        for url in image_urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                img = Image.open(response.raw)
                img.thumbnail((200, 200))
                bg_image.paste(img, (current_x, current_y))
                current_x += img.width + 10
                if current_x > composite_width - 200:
                    current_x = 10
                    current_y += img.height + 10
            except Exception as e:
                print(f"Error processing image {url}: {e}")
                continue

        return bg_image
    except Exception as e:
        print(f"Error creating composite image: {e}")
        raise

@app.route('/api/composite_image', methods=['GET'])
def get_composite_image():
    try:
        images = fetch_images()
        if not images:
            return jsonify({"error": "No images found"}), 404
        composite_image = create_composite_image(images)
        composite_image_path = os.path.join("/tmp", "composite_image.jpg")
        composite_image.save(composite_image_path)
        return send_file(composite_image_path, mimetype='image/jpeg')
    except Exception as e:
        print(f"Error in get_composite_image: {e}")
        return jsonify({"error": "Error creating composite image"}), 500

if __name__ == '__main__':
    app.run(debug=True)
