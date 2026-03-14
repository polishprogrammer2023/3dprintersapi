from flask import Flask, jsonify, request
import json, requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
def get_bambu_price():
    url = "https://eu.store.bambulab.com/pl/products/a1-mini"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Jeśli tutaj rzuci błędem 403 lub 407, będziemy wiedzieć dlaczego
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        klasy = "bbl-title-2 font-bold tabular-nums"
        element = soup.find(class_=klasy)

        if element:
            surowy_tekst = element.get_text(strip=True)
            clean_price = re.sub(r'[^\d.]', '', surowy_tekst.replace(',', '.'))
            return {"price": float(clean_price)}

        return {"error": "Nie znaleziono elementu HTML na stronie"}

    except requests.exceptions.ProxyError:
        return {"error": "Blokada PythonAnywhere (Proxy). Darmowe konta mają ograniczony dostęp do stron zewnętrznych."}
    except Exception as e:
        return {"error": str(e)}

def load_printers():
    with open("printer.json", "r") as f:
        return json.load(f)

@app.route("/printers", methods=["GET"])
def get_all_printers():
    data = load_printers()
    return jsonify(data)

@app.route("/printers/<brand>", methods=["GET"])
def get_brand(brand):
    data = load_printers()
    brand_cap = brand.capitalize()
    if brand_cap in data:
        return jsonify(data[brand_cap])
    return jsonify({"error": "Brand not found"}), 404

@app.route("/printer/<brand>/<model>", methods=["GET"])
def get_model(brand, model):
    data = load_printers()
    brand_cap = brand.capitalize()
    if brand_cap in data and model in data[brand_cap]:
        return jsonify(data[brand_cap][model])
    return jsonify({"error": "Model not found"}), 404
@app.route('/printer/Bambulab/a1-mini/price', methods=['GET'])
def get_price_endpoint():
    result = get_bambu_price()
    # Zwracamy to, co wypluje funkcja (albo cenę, albo konkretny błąd)
    status = 200 if "price" in result else 500
    return jsonify(result), status
if __name__ == "__main__":
    app.run()