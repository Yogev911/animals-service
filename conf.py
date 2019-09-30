import os

DOWNLOAD_IMAGES = True
MAX_PROCESS = os.cpu_count()
IMAGES_PATH = "tmp/"
PAGE_URL = "https://en.wikipedia.org/wiki/List_of_animal_names"

TABLE_HEADER_COLS = ["Animal",
                     "Scientific term",
                     "Young",
                     "Female",
                     "Male",
                     "Collateral adjective"]

TABLE_CLASS_NAME = "wikitable"

ADD_TH_TAG = lambda name: f"<tr>{name}</tr>"

HTML_TEMPLATE = lambda body: f"""
<!doctype html>

<html lang="en">
<head>
</head>

<body>
  {body}
</body>
</html>
"""
