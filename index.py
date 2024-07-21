def fetch_images():
    url = "https://apexitemstore.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
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
    except Exception as e:
        print(f"Error fetching images: {e}")
        raise
