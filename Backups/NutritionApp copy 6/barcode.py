# barcode.py
import cv2
from pyzbar.pyzbar import decode
import requests

class BarcodeScanner:
    def __init__(self):
        self.scanned_items = {}

    def fetch_nutritional_data(self, barcode_data):
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode_data}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching data for barcode {barcode_data}")
            return None

    def display_nutritional_info(self, nutritional_data):
        if nutritional_data and nutritional_data.get("status") == 1:
            product = nutritional_data.get("product", {})
            product_name = product.get("product_name", "Unknown")
            description = product.get("generic_name", "Description not available")
            expiration_date = product.get("expiration_date", "Not specified")
            if expiration_date == "Not specified":
                expiration_date = "Expiry date not available"
            calories = product.get("nutriments", {}).get("energy-kcal_100g", "Calories not specified")
            allergens = product.get("allergens_tags", ["None listed"])
            ingredients = product.get("ingredients_text", "Ingredients not specified")

            info = {
                "product_name": product_name,
                "description": description,
                "expiration_date": expiration_date,
                "calories": calories,
                "allergens": allergens,
                "ingredients": ingredients,
            }
            return info
        else:
            print("No information available for this barcode.")
            return None

    def scan_barcode(self, image_path):
        frame = cv2.imread(image_path)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray)

        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")
            barcode_type = obj.type
            if barcode_data not in self.scanned_items:
                print(f"Barcode: {barcode_data}, Type: {barcode_type}")
                nutritional_data = self.fetch_nutritional_data(barcode_data)
                info = self.display_nutritional_info(nutritional_data)
                self.scanned_items[barcode_data] = info
                return info
        return None 