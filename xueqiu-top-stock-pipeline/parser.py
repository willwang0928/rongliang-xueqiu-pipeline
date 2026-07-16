from html import unescape
from bs4 import BeautifulSoup
from datetime import datetime

def clean_html(value):
    if not value:
        return ""
    text = BeautifulSoup(value, "html.parser").get_text(" ", strip=True)
    return unescape(" ".join(text.split()))

def format_created_at(value):
    if not value:
        return ""
    return datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d %H:%M:%S")
    
def parse_post(raw, stock=''):
    user = raw.get('user') or {}
    return {
        'stock': stock,
        'name': user.get('screen_name', ''),
        'date': format_created_at(raw.get('created_at')),
        'content': clean_html(raw.get('text')),
    }

def parse_posts(raw_posts, stock=''):
    return [parse_post(raw, stock) for raw in raw_posts]

