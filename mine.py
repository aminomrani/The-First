import requests
import time
import re
import logging
from v2ray_util import V2RayClient, V2RayConfigError

# Logging settings
logging.basicConfig(filename="error_log.txt",
                    level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def download_file(url):
    """Download a text file from a given URL and return its content as a list of lines."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return response.text.splitlines()
    except requests.RequestException as e:
        logging.error(f"Failed to download file from {url}. Error: {e}")
        return []

def extract_v2ray_configs(lines):
    """Extract V2Ray configuration links from a list of lines."""
    configs = []
    # Regular expression for V2Ray config links
    v2ray_pattern = r"(vmess://|vless://|trojan://|ss://)[^\s]+"
    for line in lines:
        matches = re.findall(v2ray_pattern, line)
        configs.extend(matches)
    return configs

def check_v2ray_link(link):
    """Check the V2Ray link using the v2ray-python library."""
    try:
        # Create a V2Ray client with the configuration link
        client = V2RayClient(link)
        # Check the connection
        result = client.ping()
        if result:
            print(f"Link is accessible: {link}")
            return True
        else:
            print(f"Link is unreachable: {link}")
            return False
    except V2RayConfigError as e:
        logging.error(f"Invalid V2Ray config format for link {link}. Error: {e}")
        return False
    except Exception as e:
        logging.error(f"Failed to check link {link}. Error: {e}")
        return False

def filter_configs(url, file_name):
    """Download file from URL, filter accessible configs, and save to a new file."""
    lines = download_file(url)
    if not lines:  # If downloading the file failed
        logging.error(f"No data found or download failed for {url}")
        return

    configs = extract_v2ray_configs(lines)
    accessible_configs = []

    for config in configs:
        if check_v2ray_link(config):
            accessible_configs.append(config)

    try:
        # Save filtered configs to a new file
        filtered_file_path = f"{file_name}_filtered.txt"
        with open(filtered_file_path, 'w') as file:
            file.write("\n".join(accessible_configs))
        print(f"Filtered configs saved to {filtered_file_path}")
    except IOError as e:
        logging.error(f"Failed to write filtered configs to file {filtered_file_path}. Error: {e}")

def process_files_in_interval(urls, interval_minutes=5):
    """Process URLs at specified interval, filter accessible configs, and save results."""
    while True:
        for index, url in enumerate(urls, start=1):
            print(f"Processing URL {index}: {url}")
            filter_configs(url, f"file{index}")
        print(f"Waiting {interval_minutes} minutes before next check...")
        time.sleep(interval_minutes * 60)

# List of URLs to download text files from
urls = [
    "https://example.com/file1.txt",  # Replace with actual URLs
    "https://example.com/file2.txt"
]
interval_minutes = 5  # Set interval for checking in minutes

# Start the process
process_files_in_interval(urls, interval_minutes)
