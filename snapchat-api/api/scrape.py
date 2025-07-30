from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/api/scrape')
def scrape():
    username = request.args.get('username', '').strip()
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        url = f"https://www.snapchat.com/add/{username}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        snapcode_img = soup.find("img", {"class": "snapcode"})["src"]
        bitmoji_img = soup.find("img", {"alt": "Bitmoji avatar"})["src"]

        return jsonify({
            "username": username,
            "snapcode": snapcode_img,
            "bitmoji": bitmoji_img
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
