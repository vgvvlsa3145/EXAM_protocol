import os
import urllib.request
import re

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts')

google_css_url = "https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&display=swap"
css_content = ""

print(f"Fetching {google_css_url}...")
req = urllib.request.Request(google_css_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

try:
    with urllib.request.urlopen(req) as response:
        css_content = response.read().decode('utf-8')
        
    # Find all url(...) in the CSS
    urls = re.findall(r"url\((https://[^)]+)\)", css_content)
    
    for url in urls:
        filename = url.split('/')[-1]
        target_path = os.path.join(FONTS_DIR, filename)
        
        print(f"Downloading {filename} from {url}...")
        font_req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(font_req) as font_resp:
            with open(target_path, 'wb') as f:
                f.write(font_resp.read())
        
        # Replace the URL in CSS with local path
        css_content = css_content.replace(url, f"../fonts/{filename}")
        
    # Save the modified CSS
    css_path = os.path.join(CSS_DIR, 'dancing-script.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
        
    print(f"Saved {css_path}")

except Exception as e:
    print(f"Error: {e}")
