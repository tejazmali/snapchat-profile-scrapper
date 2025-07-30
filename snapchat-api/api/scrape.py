from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os, base64, re, requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/api/scrape")
def scrape(username: str):
    username = username.strip()
    result = {
        "username": username,
        "snapcode_svg_url": f"https://app.snapchat.com/web/deeplink/snapcode?username={username}&type=SVG&bitmoji=enable",
        "bitmoji_image_url": None,
        "bitmoji_3d_render_url": None,
        "background_image_url": None,
        "display_name": None
    }

    try:
        svg_text = requests.get(result["snapcode_svg_url"]).text
        soup = BeautifulSoup(svg_text, "xml")
        img = soup.find("image")
        href = img.get("xlink:href") or img.get("href")
        if href and href.startswith("data:image/png;base64,"):
            result["bitmoji_image_base64"] = href

        res = requests.get(f"https://www.snapchat.com/add/{username}", headers={"User-Agent": "Mozilla/5.0"})
        html = res.text

        render_match = re.search(r'(https://[^"]+/render/[^"]+\.webp)', html)
        if render_match:
            result["bitmoji_3d_render_url"] = render_match.group(1)

        bg_match = re.search(r'(https://[^"]+/background/[^"]+\.webp)', html)
        if bg_match:
            result["background_image_url"] = bg_match.group(1)

        soup = BeautifulSoup(html, "html.parser")
        name_tag = soup.find("h4", class_="Heading_h400Emphasis__SQXxl")
        if name_tag:
            result["display_name"] = name_tag.text.strip()

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return result
