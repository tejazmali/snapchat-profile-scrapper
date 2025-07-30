from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/snapchat', methods=['GET'])
def snapchat_scraper():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    result = {
        "username": username,
        "snapcode_url": f"https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG&bitmoji=enable",
        "bitmoji_base64_url": None,
        "3d_bitmoji_url": None,
        "background_image_url": None,
        "display_name": None,
        "status": "partial"
    }

    # ---------- 1. Snapcode SVG (to extract base64 Bitmoji) ----------
    try:
        svg_url = f"https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG&bitmoji=enable"
        svg_res = requests.get(svg_url, timeout=10)
        svg_res.raise_for_status()

        soup = BeautifulSoup(svg_res.text, "xml")

        # Detect both href and xlink:href
        image_tag = soup.find("image")
        if image_tag:
            data_uri = image_tag.get("xlink:href") or image_tag.get("href")
            if data_uri and data_uri.startswith("data:image/png;base64,"):
                result["bitmoji_base64_url"] = data_uri
    except Exception as e:
        result["bitmoji_error"] = str(e)

    # ---------- 2. Profile Page (to extract 3D Bitmoji, background, and display name) ----------
    try:
        profile_url = f"https://www.snapchat.com/@{username}"
        prof_res = requests.get(profile_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        prof_res.raise_for_status()
        html = prof_res.text

        # 3D Bitmoji
        render_match = re.search(r'https://[^"]+/render/[^"]+\.webp', html)
        if render_match:
            result["3d_bitmoji_url"] = render_match.group(0)

        # Background image
        bg_match = re.search(r'https://[^"]+/background/[^"]+\.webp', html)
        if bg_match:
            result["background_image_url"] = bg_match.group(0)

        # Display name
        soup = BeautifulSoup(html, "html.parser")
        display_name_tag = soup.find("h4", class_="Heading_h400Emphasis__SQXxl")
        if display_name_tag:
            result["display_name"] = display_name_tag.get_text(strip=True)

        result["status"] = "success"
    except Exception as e:
        result["profile_error"] = str(e)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)