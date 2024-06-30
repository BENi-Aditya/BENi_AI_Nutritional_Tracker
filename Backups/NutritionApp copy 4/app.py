from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import cv2
import os
import base64
import numpy as np
import requests
import openai
from pyzbar.pyzbar import decode  # Importing the decode function

app = Flask(__name__)

openai.api_key = 'sk-proj-zwthpQecL2ERMxGVTqyxT3BlbkFJWujkjC3fNdAImjPeask3'

user_data = {}
scanned_data = {}
SAVE_PATH = "/Users/tripathd/Downloads/Nutrition/Barcode scans"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

@app.route('/')
def entry():
    return render_template('entry.html')

@app.route('/save_user_data', methods=['POST'])
def save_user_data():
    global user_data
    user_data = request.form.to_dict()
    print(f"User data saved: {user_data}")
    return redirect(url_for('scan'))

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/capture_frame', methods=['POST'])
def capture_frame():
    try:
        data = request.json['image']
        image_data = base64.b64decode(data.split(',')[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        image_path = os.path.join(SAVE_PATH, 'captured_frame.jpg')
        cv2.imwrite(image_path, frame)
        
        product_info = scan_barcode(image_path)
        if product_info:
            global scanned_data
            scanned_data = product_info
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'message': 'No barcode found', 'status': 'failed'}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed with an unknown error', 'status': 'failed'}), 500

@app.route('/product')
def product():
    global scanned_data
    barcode_data = scanned_data.get('barcode', None)
    if barcode_data:
        nutritional_data = fetch_nutritional_data(barcode_data)
        scanned_data.update({
            'product_name': nutritional_data.get('product_name', 'Unknown'),
            'ingredients': nutritional_data.get('ingredients_text', 'Not specified').split(', '),
            'nutrients': nutritional_data.get('nutriments', {}),
        })
    return render_template('product.html', product=scanned_data, user=user_data)

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/ask_chatgpt', methods=['POST'])
def ask_chatgpt():
    user_question = request.form['question']
    prompt = f"Product: {scanned_data.get('product_name', 'Unknown')}\nDescription: {scanned_data.get('description', '')}\nUser Question: {user_question}"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=150
    )
    answer = response.choices[0].text.strip()
    return jsonify({'answer': answer})

def fetch_nutritional_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('product', {})
    else:
        return {}

def scan_barcode(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = decode(gray)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        return fetch_nutritional_data(barcode_data)
    return {}

if __name__ == '__main__':
    app.run(debug=True)
