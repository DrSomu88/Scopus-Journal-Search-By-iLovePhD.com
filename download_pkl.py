import os
import gdown

# Read file ID from environment variable
file_id = os.getenv("DRIVE_FILE_ID")
if not file_id:
    raise ValueError("DRIVE_FILE_ID environment variable not set.")

url = f"https://drive.google.com/uc?id={file_id}"
output = "scopus_search_index.pkl"

print(f"Downloading from {url}...")
gdown.download(url, output, quiet=False)
print("Download complete.")
