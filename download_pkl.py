import os
import gdown

FILE_ID = os.getenv("19kBbAjIX5ZV1vywEVrpKTAqBN73FV7vK")  # or DRIVE_FOLDER_ID
if not os.path.exists("search_index.pkl"):
    url = f"https://drive.google.com/uc?id={FILE_ID}"
    gdown.download(url, "scopus_search_index.pkl", quiet=False)
