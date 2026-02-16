import os


class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    USER_CSV_PATH = os.path.join(BASE_DIR, "data", "users.csv")
    DB_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")
    LOG_PATH = os.path.join(BASE_DIR, "data", "app.log")
    POSTS_API_URL = "https://jsonplaceholder.typicode.com/posts"
    CHUNK_SIZE = 10
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
    SAVE_POSTS_URL = f"http://{API_HOST}:{API_PORT}/save-posts"
    EXTERNAL_WEBHOOK_URL = f"http://{API_HOST}:{API_PORT}/save-posts"