import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.utils import get_platform_info, get_mac_address

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
platform, device = get_platform_info(ua)
print(f"Test UA: {ua}")
print(f"Detected Platform: {platform}, Device: {device}")

mac = get_mac_address("127.0.0.1")
print(f"Detected MAC for localhost: {mac}")

mac2 = get_mac_address("192.168.1.1") # Dummy IP for test
print(f"Detected MAC for dummy IP: {mac2}")
