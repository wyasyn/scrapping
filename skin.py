import requests
from bs4 import BeautifulSoup
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

condition_urls = {
    'Acne': 'https://getskinbeauty.com/skincare/acne/?_acne=acne',
    'Aging': 'https://getskinbeauty.com/skincare/aging/?_aging=aging',
    'Dryness': 'https://getskinbeauty.com/skincare/dryness/?_dryness=dryness',
    'Pigmentation': 'https://getskinbeauty.com/skincare/pigmentation/?_pigmentation=pigmentation',
    'Oil Control': 'https://getskinbeauty.com/skincare/oil-control/?_oil_control=oil-control',
    'Post Procedure': 'https://getskinbeauty.com/skincare/post-procedure/?_post_procedure=post-procedure',
    'Sun Care': 'https://getskinbeauty.com/skincare/suncare/?_suncare=sun-care'
}

all_conditions = []

for condition_name, url in condition_urls.items():
    print(f"\n🔍 Scraping condition: {condition_name} ({url})")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 🧾 Get title
    title_tag = soup.find('h1', class_='elementor-heading-title elementor-size-default')
    title = title_tag.text.strip() if title_tag else condition_name

    # 📘 Get description from a specific data-id container
    description = 'No description found'

    # Find the container using the data-id attribute
    target_div = soup.find('div', attrs={'data-id': '316efeba'})

    if target_div:
        # Find the elementor-widget-container inside it
        desc_div = target_div.find('div', class_='elementor-widget-container')
        
        if desc_div:
            description = desc_div.get_text(separator=' ', strip=True)


    # 🛍️ Find recommended products
    product_grid = soup.find('div', class_='elementor-loop-container elementor-grid')
    recommended_products = []

    if product_grid:
        product_items = product_grid.find_all(
            'div',
            attrs={
                'data-elementor-type': 'loop-item',
                'data-elementor-id': '4408'
            }
        )

        for product in product_items:
            a_tag = product.find('a', href=True)
            link = a_tag['href'] if a_tag else 'No Link'

            title_tag = product.find('h3', class_='product_title entry-title elementor-heading-title elementor-size-default')
            product_title = title_tag.text.strip() if title_tag else 'No Title'

            price_tag = product.find('span', class_='woocommerce-Price-amount amount')
            price = price_tag.text.strip() if price_tag else 'No Price'

            img_tag = product.find('img')
            image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else 'No Image'

            # Fetch full description + ingredients
            full_description = 'No description'
            ingredients = []

            if link != 'No Link':
                try:
                    detail_resp = requests.get(link, headers=headers)
                    detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

                    desc_section = detail_soup.find('div', id='tab-description')
                    if desc_section:
                        paragraphs = desc_section.find_all('p')
                        if len(paragraphs) >= 2:
                            full_description = paragraphs[1].get_text(strip=True)

                    ing_div = detail_soup.find('div', id='tab-ingredients')
                    if ing_div:
                        for tag in ing_div.find_all(['h2', 'strong']):
                            tag.decompose()

                        p_tag = ing_div.find('p')
                        if p_tag:
                            raw_ingredients = p_tag.get_text(separator=' ', strip=True)
                            ingredients = [i.strip() for i in raw_ingredients.split('•') if i.strip()]

                except Exception as e:
                    print(f"⚠️ Failed to scrape product detail {link}: {e}")

            recommended_products.append({
                'title': product_title,
                'price': price,
                'description': full_description,
                'ingredients': ingredients,
                'image_url': image_url,
                'link': link
            })

    all_conditions.append({
        'condition': title,
        'description': description,
        'recommended_products': recommended_products
    })

    print(f"✅ Collected {len(recommended_products)} products for {condition_name}")
    time.sleep(1)  # Be respectful to the server

# Save everything
with open('skin_conditions.json', 'w', encoding='utf-8') as f:
    json.dump(all_conditions, f, ensure_ascii=False, indent=4)

print(f"\n🎉 Done scraping! Total conditions: {len(all_conditions)}")
