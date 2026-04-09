import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

with app.test_client() as client:
    resp = client.get('/class/1/dashboard')
    html = resp.get_data(as_text=True)
    start = html.find('<table')
    print(html[start:start+1200])
