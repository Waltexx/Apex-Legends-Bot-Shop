import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

def fetch_images():
    url = "https://apexitemstore.com/"
    base_url = "https://apexitemstore.com"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
    except RequestException as e:
        return {"error": f"Échec de la récupération de la page. Erreur : {e}"}
    
    try:
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        return {"error": f"Échec de l'analyse du contenu de la page. Erreur : {e}"}

    sections = ["Featured", "Monthly", "Exotic Shop", "Recolors", "Corrupted Summer store"]
    images_by_section = {section: [] for section in sections}

    for section in sections:
        try:
            if section == "Corrupted Summer store":
                # Directly scrape the Corrupted Summer store section
                corrupted_summer_url = f"{base_url}/corrupted-summer-store"
                corrupted_response = requests.get(corrupted_summer_url)
                corrupted_response.raise_for_status()
                corrupted_soup = BeautifulSoup(corrupted_response.content, "html.parser")
                images = corrupted_soup.find_all('img')
                image_links = [img.get('src') for img in images if img.get('src')]
                image_links = [link if link.startswith('http') else base_url + link for link in image_links]
                images_by_section[section].extend(image_links)
            else:
                section_header = soup.find('h3', string=section)
                if section_header:
                    paragraph = section_header.find_next('p')
                    if paragraph:
                        images = paragraph.find_all('img')
                        image_links = [img.get('src') for img in images if img.get('src')]
                        image_links = [link if link.startswith('http') else base_url + link for link in image_links]
                        images_by_section[section].extend(image_links)
        except Exception as e:
            images_by_section[section].append(f"Erreur lors du traitement de la section '{section}'. Erreur : {e}")

    return images_by_section

@app.route('/api/shop', methods=['GET'])
def get_images():
    images = fetch_images()
    return jsonify(images)

# Vercel expects the app to be defined in `index.py`
# No need to specify port and `app.run()` for Vercel deployments
