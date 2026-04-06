import subprocess
import re
import platform

def get_mac_address(ip_address):
    """
    Attempts to retrieve the MAC address for a given IP address
    by scanning the system's ARP table.
    Works best on local networks (LAN).
    """
    if ip_address in ['127.0.0.1', '::1', 'localhost']:
        import uuid
        mac_num = hex(uuid.getnode()).replace('0x', '').zfill(12)
        mac = ":".join(mac_num[i:i+2] for i in range(0, 12, 2)).upper()
        return mac
    try:
        if platform.system().lower() == 'windows':
            # Ping first to ensure ARP table is populated for active clients
            subprocess.run(f"ping -n 1 -w 200 {ip_address}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Windows: arp -a [IP]
            cmd = f"arp -a {ip_address}"
            output = subprocess.check_output(cmd, shell=True).decode('ascii', errors='ignore')
            
            # Look for typical Physical Address string format
            mac_regex = r"([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})"
            match = re.search(mac_regex, output)
            if match:
                return match.group(0).replace('-', ':').upper()
        else:
            subprocess.run(f"ping -c 1 -W 1 {ip_address}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Linux/Mac: arp -n [IP]
            cmd = f"arp -n {ip_address}"
            output = subprocess.check_output(cmd, shell=True).decode('ascii', errors='ignore')
            mac_regex = r"([0-9a-fA-F]{2}[:][0-9a-fA-F]{2}[:][0-9a-fA-F]{2}[:][0-9a-fA-F]{2}[:][0-9a-fA-F]{2}[:][0-9a-fA-F]{2})"
            match = re.search(mac_regex, output)
            if match:
                return match.group(0).upper()
                
    except Exception as e:
        print(f"Error retrieving MAC for {ip_address}: {e}")
        
    return "UNKNOWN"

def get_platform_info(user_agent):
    """
    Parses the user agent to extract platform (OS) and basic device info.
    """
    ua = user_agent.lower()
    
    # Platform Detection
    if 'windows phon' in ua: platform = "Windows Phone"
    elif 'android' in ua: platform = "Android"
    elif 'iphone' in ua or 'ipad' in ua: platform = "iOS"
    elif 'windows' in ua: platform = "Windows"
    elif 'macintosh' in ua: platform = "macOS"
    elif 'linux' in ua: platform = "Linux"
    else: platform = "Unknown Platform"
    
    # Device/Browser Hint
    device = "Web Browser"
    # Order matters for accurate matching
    if 'postman' in ua: device = "Postman"
    elif 'edg' in ua: device = "Microsoft Edge"
    elif 'opr' in ua or 'opera' in ua: device = "Opera"
    elif 'chrome' in ua and 'chrom' in ua: device = "Google Chrome"
    elif 'safari' in ua and 'chrome' not in ua: device = "Apple Safari"
    elif 'firefox' in ua: device = "Mozilla Firefox"
    elif 'trident' in ua or 'msie' in ua: device = "Internet Explorer"
    
    return platform, device
