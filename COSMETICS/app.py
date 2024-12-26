import json
import requests
from datetime import datetime
from flask import Flask, render_template

app = Flask(__name__)

# Tu clave API de fortniteapi.io
API_KEY = '107a1219-96c01308-f4569489-336df56e'

# URL de la API de fortniteapi.io
API_URL = 'https://fortniteapi.io/v2/shop?lang=es'

# Función para obtener los datos de la API
def get_data():
    headers = {'Authorization': API_KEY}
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"shop": []}

# Función para convertir la fecha de fin en un objeto datetime
def get_end_date(item):
    return datetime.fromisoformat(item["offerDates"]["out"].replace('Z', '+00:00'))

# Función para limpiar la fecha de fin
def clean_end_date(end_date):
    return end_date.replace('T00:00:00.000Z', '').replace('T23:59:59.999Z', '').replace("T00:00:00Z", "")

# Función para calcular el precio en USD
def calculate_price(finalPrice):
    return ((finalPrice * 0.46) / 100) - 0.25

@app.route('/')
def index():
    data = get_data()
    # Ordenar los datos por la fecha de fin
    sorted_data = sorted(data["shop"], key=get_end_date)

    # Agrupar los datos por secciones
    grouped_data = {}
    for item in sorted_data:
        section_name = item["section"]["name"] if "section" in item and item["section"] else "Sin Sección"
        if section_name not in grouped_data:
            grouped_data[section_name] = []
        item['offer_end_date'] = clean_end_date(item["offerDates"]["out"])
        item['full_background'] = item["displayAssets"][0].get("full_background", "N/A")
        item['price_usd'] = calculate_price(item["price"]["finalPrice"])
        grouped_data[section_name].append(item)

    # Orden de los tipos principales
    type_order = [
        "bundle", "outfit", "backpack", "pickaxe",
        "emote", "glider", "wrap", "sparks_song",
        "shoes", "vehicle_booster", "sparks_bass",
        "sparks_guitar", "sparks_keyboard", "sparks_microphone", "building_set", "sparks_drum"
    ]

    # Ordenar los items dentro de cada sección según el tipo principal
    for section in grouped_data:
        grouped_data[section] = sorted(grouped_data[section], key=lambda x: type_order.index(x["mainType"]) if "mainType" in x else len(type_order))

    return render_template('index.html', data=grouped_data)

if __name__ == '__main__':
    app.run(debug=True)