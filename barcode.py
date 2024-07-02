import cv2
from pyzbar.pyzbar import decode
import requests

class BarcodeScanner:
    def scan_barcode(self, image_path):
        barcode_data = self.decode_barcode(image_path)
        if barcode_data:
            return self.fetch_nutritional_data(barcode_data)
        return None

    def decode_barcode(self, image_path):
        img = cv2.imread(image_path)
        barcodes = decode(img)
        for barcode in barcodes:
            return barcode.data.decode('utf-8')
        return None

    def fetch_nutritional_data(self, barcode):
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get('product', {})
            important_ingredients = [ingredient['text'] for ingredient in data.get('ingredients', []) if ingredient.get('percent_estimate', 0) > 5]
            allergens = data.get('allergens_tags', ['None listed'])
            dietary = 'Vegan' if 'en:vegan' in data.get('labels_tags', []) else 'Vegetarian' if 'en:vegetarian' in data.get('labels_tags', []) else 'Non-Vegetarian'
            return {
                'product_name': data.get('product_name', 'Unknown Product'),
                'image_url': data.get('image_url', ''),
                'description': data.get('generic_name', 'No description available'),
                'expiration_date': data.get('expiration_date', 'Not specified'),
                'calories': data.get('nutriments', {}).get('energy-kcal_100g', 'Not specified'),
                'allergens': ', '.join(allergens),
                'important_ingredients': ', '.join(important_ingredients),
                'dietary': dietary,
                'ingredients': ', '.join(important_ingredients)  # Ensure ingredients data is passed
            }
        return {}
