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
            return data.get('product', {})
        else:
            print(f"Error fetching data for barcode {barcode_data}")
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
                if nutritional_data:
                    self.scanned_items[barcode_data] = nutritional_data
                    return nutritional_data
        
        return None
