def create_composite_image(image_urls):
    try:
        bg_path = "Background.png"  # Chemin relatif
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
    except Exception as e:
        print(f"Error creating composite image: {e}")
        raise
