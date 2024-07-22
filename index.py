import requests
from flask import Flask, send_file, jsonify
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
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        section = "Corrupted Summer Store"
        section_header = soup.find('h3', string=section)
        if section_header:
            next_element = section_header.find_next()
            while next_element and next_element.name not in ['ul', 'p']:
                next_element = section_header.find_next()
            if next_element:
                return [img.get('src') for img in next_element.find_all('img') if img.get('src')]
        return []
    except Exception as e:
        print(f"Error fetching images: {e}")
        return []

def create_composite_image(image_urls):
    try:
        # Load the background image
        bg_path = "Background.png"
        if not os.path.exists(bg_path):
            raise FileNotFoundError(f"Background image not found at {bg_path}")

        bg_image = Image.open(bg_path)
        bg_width, bg_height = bg_image.size

        # Variables to compute the required size of the composite image
        margin = 10
        max_width = bg_width
        current_x, current_y = margin, margin
        row_height = 0
        total_height = margin

        # Determine the required height of the composite image
        for url in image_urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                img = Image.open(response.raw)
                img.thumbnail((bg_width // 5, bg_height // 5))  # Resize proportionally
                
                if current_x + img.width > max_width - margin:
                    current_x = margin
                    current_y += row_height + margin
                    total_height = current_y
                    row_height = 0
                
                row_height = max(row_height, img.height)
                current_x += img.width + margin
            except Exception as e:
                print(f"Error processing image {url}: {e}")
                continue

        # Create a new image with the calculated dimensions
        total_height = max(total_height + row_height + margin, bg_height)
        composite_image = Image.new('RGB', (bg_width, total_height), (255, 255, 255))
        composite_image.paste(bg_image, (0, 0))

        # Draw images onto the composite image
        current_x, current_y = margin, margin
        row_height = 0

        for url in image_urls:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                img = Image.open(response.raw)
                img.thumbnail((bg_width // 5, bg_height // 5))
                
                if current_x + img.width > max_width - margin:
                    current_x = margin
                    current_y += row_height + margin
                    row_height = 0
                
                composite_image.paste(img, (current_x, current_y))
                current_x += img.width + margin
                row_height = max(row_height, img.height)
            except Exception as e:
                print(f"Error processing image {url}: {e}")
                continue

        return composite_image
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
