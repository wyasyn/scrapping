import requests
from bs4 import BeautifulSoup
import json
import time

base_url = 'https://getskinbeauty.com/skincare'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

all_products = []
page = 1

while True:
    url = base_url if page == 1 else f'{base_url}/page/{page}/'
    print(f'🔍 Scraping Page {page}: {url}')

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_grid = soup.find('div', class_='elementor-loop-container elementor-grid')
    if not product_grid:
        print(f"❌ No product grid found on page {page}. Ending scrape.")
        break

    product_items = product_grid.find_all(
        'div',
        attrs={
            'data-elementor-type': 'loop-item',
            'data-elementor-id': '4408'
        }
    )

    if not product_items:
        print(f"✅ Reached end of paginated content at page {page}.")
        break

    for product in product_items:
        a_tag = product.find('a', href=True)
        link = a_tag['href'] if a_tag else 'No Link'

        title_tag = product.find('h3', class_='product_title entry-title elementor-heading-title elementor-size-default')
        title = title_tag.text.strip() if title_tag else 'No Title'

        price_tag = product.find('span', class_='woocommerce-Price-amount amount')
        price = price_tag.text.strip() if price_tag else 'No Price'

        img_tag = product.find('img')
        image_url = img_tag['src'] if img_tag and img_tag.has_attr('src') else 'No Image'

        # 📝 Get full description from detail page
        full_description = 'No description'
        ingredients = []

        if link != 'No Link':
            try:
                detail_resp = requests.get(link, headers=headers)
                detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

                # 📘 Description: get second <p> in #tab-description
                desc_div = detail_soup.find('div', id='tab-description')
                if desc_div:
                    desc_paragraphs = desc_div.find_all('p')
                    if len(desc_paragraphs) >= 2:
                        full_description = desc_paragraphs[1].get_text(strip=True)

                # 🧪 Ingredients: get cleaned <p> in #tab-ingredients
                ing_div = detail_soup.find('div', id='tab-ingredients')
                if ing_div:
                    # Remove h2 and strong tags
                    for tag in ing_div.find_all(['h2', 'strong']):
                        tag.decompose()

                    p_tag = ing_div.find('p')
                    if p_tag:
                        raw_ingredients = p_tag.get_text(separator=' ', strip=True)
                        ingredients = [i.strip() for i in raw_ingredients.split('•') if i.strip()]

            except Exception as e:
                print(f"⚠️ Error scraping detail page for {link}: {e}")


        all_products.append({
            'title': title,
            'price': price,
            'description': full_description,
            'ingredients': ingredients,
            'image_url': image_url,
            'link': link
        })


    print(f"✅ Scraped {len(product_items)} products from page {page}")
    page += 1
    time.sleep(1)  # 😴 Be nice to the server

# Save to JSON
with open('products.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=4)

print(f"\n🎉 Finished scraping. Total products collected: {len(all_products)}")
