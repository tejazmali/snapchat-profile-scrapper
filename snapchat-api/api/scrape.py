# /api/scrape.py

from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import json
from bs4 import BeautifulSoup

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        username = query_params.get("username", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if not username:
            self.wfile.write(json.dumps({"error": "Missing username"}).encode())
            return

        try:
            res = requests.get(f"https://www.snapchat.com/add/{username}")
            soup = BeautifulSoup(res.text, 'html.parser')

            snapcode = soup.find("img", {"alt": "Snapcode"})["src"]
            bitmoji = soup.find("img", {"class": lambda x: x and "bitmoji" in x})["src"]

            output = {
                "username": username,
                "snapcode": snapcode,
                "bitmoji": bitmoji
            }

            self.wfile.write(json.dumps(output).encode())

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
