from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

@app.route('/api/snapchat', methods=['GET'])
def snapchat_scraper():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    result = {
        "username": username,
        "snapcode_svg_url": f"https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG&bitmoji=enable",
        "bitmoji_image_base64": None,
        "3d_bitmoji_url": None,
        "background_image_url": None,
        "display_name": None,
        "status": "partial"
    }

    # Fetch Snapcode SVG and extract base64 Bitmoji
    try:
        svg_res = requests.get(result["snapcode_svg_url"], timeout=10)
        svg_res.raise_for_status()
        soup = BeautifulSoup(svg_res.text, "xml")
        image_tag = soup.find("image")
        if image_tag:
            data_uri = image_tag.get("xlink:href") or image_tag.get("href")
            if data_uri and data_uri.startswith("data:image/png;base64,"):
                result["bitmoji_image_base64"] = data_uri
    except Exception as e:
        result["bitmoji_error"] = str(e)

    # Scrape Snapchat public profile page
    try:
        profile_url = f"https://www.snapchat.com/@{username}"
        prof_res = requests.get(profile_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        prof_res.raise_for_status()
        html = prof_res.text

        render_match = re.search(r'https://[^"]+/render/[^"]+\.webp', html)
        if render_match:
            result["3d_bitmoji_url"] = render_match.group(0)

        bg_match = re.search(r'https://[^"]+/background/[^"]+\.webp', html)
        if bg_match:
            result["background_image_url"] = bg_match.group(0)

        soup = BeautifulSoup(html, "html.parser")
        display_name_tag = soup.find("h4", class_="Heading_h400Emphasis__SQXxl")
        if display_name_tag:
            result["display_name"] = display_name_tag.get_text(strip=True)

        result["status"] = "success"
    except Exception as e:
        result["profile_error"] = str(e)

    return jsonify(result)
