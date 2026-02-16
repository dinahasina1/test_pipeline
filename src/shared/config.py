import os


class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    USER_CSV_PATH = os.path.join(BASE_DIR, "data", "users.csv")
    DB_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")
    POSTS_API_URL = "https://jsonplaceholder.typicode.com/posts"
    CHUNK_SIZE = 10
    EXTERNAL_WEBHOOK_URL = "https://webhook.site/votre-id-unique"
    API_HOST = "0.0.0.0"
    API_PORT = 8000
