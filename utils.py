import json

with open('skin_conditions.json', encoding='utf-8') as f:
    json_data = json.load(f)
    
    
def get_recommended_products(data, condition_query):
    # Normalize the query for case-insensitive comparison
    condition_query = condition_query.strip().lower()
    
    for entry in data:
        if entry.get("condition", "").strip().lower() == condition_query:
            return entry.get("recommended_products", [])
    
    return []  # Return empty list if condition not found

# Example condition search
condition = "aging"
recommended = get_recommended_products(json_data, condition)

for product in recommended:
    print(f"- {product['title']} ({product['price']})")










