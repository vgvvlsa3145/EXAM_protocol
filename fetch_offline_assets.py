import os
import urllib.request
from urllib.error import URLError

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
JS_DIR = os.path.join(STATIC_DIR, 'js')
FONTS_DIR = os.path.join(STATIC_DIR, 'fonts') # For bootstrap icons

os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(JS_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

assets = {
    'css': [
        ('bootstrap.min.css', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'),
        ('bootstrap-icons.css', 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'),
    ],
    'js': [
        ('bootstrap.bundle.min.js', 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'),
        ('jquery-3.6.0.min.js', 'https://code.jquery.com/jquery-3.6.0.min.js'),
        ('chart.js', 'https://cdn.jsdelivr.net/npm/chart.js'),
    ],
    'fonts': [
        ('bootstrap-icons.woff2', 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2'),
        ('bootstrap-icons.woff', 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff'),
    ]
}

print("Starting localized asset download...")

for category, items in assets.items():
    for filename, url in items:
        if category == 'css':
            target_path = os.path.join(CSS_DIR, filename)
        elif category == 'js':
            target_path = os.path.join(JS_DIR, filename)
        else:
            target_path = os.path.join(FONTS_DIR, filename)
            
        print(f"Downloading {filename}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                content = response.read()
                
                # If it's bootstrap-icons.css, fix the relative font paths
                if filename == 'bootstrap-icons.css':
                    content_str = content.decode('utf-8')
                    content_str = content_str.replace('./fonts/', '../fonts/')
                    content = content_str.encode('utf-8')
                    
                with open(target_path, 'wb') as f:
                    f.write(content)
            print(f" -> Saved to {target_path}")
        except Exception as e:
            print(f" -> ERROR downloading {filename}: {e}")

# Special handling for Google Font (Dancing Script)
print("Downloading Dancing Script font...")
font_url = "https://fonts.gstatic.com/s/dancingscript/v24/If2cXTr6YS-zF4S-kcSWSVi_szLviuEMVQ.woff2" # Direct woff2 link
target_font_path = os.path.join(FONTS_DIR, "dancing-script.woff2")
try:
    req = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open(target_font_path, 'wb') as f:
            f.write(response.read())
    print(f" -> Saved to {target_font_path}")
    
    # Create the CSS for it
    custom_font_css = """
    @font-face {
      font-family: 'Dancing Script';
      font-style: normal;
      font-weight: 700;
      font-display: swap;
      src: url('../fonts/dancing-script.woff2') format('woff2');
    }
    """
    with open(os.path.join(CSS_DIR, 'dancing-script.css'), 'w') as f:
        f.write(custom_font_css)
    print(" -> Created local dancing-script.css")
except Exception as e:
    print(f" -> ERROR downloading Dancing Script: {e}")

print("\nAsset download complete! Next, update the HTML templates.")
