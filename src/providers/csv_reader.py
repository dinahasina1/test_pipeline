import csv
from typing import Dict
from src.core.models import User

def load_users_map(file_path: str) -> Dict[int, User]:
    """
    Reads the CSV and returns a mapping of userId -> User object.
    Indexed for fast lookup during stream processing.
    """
    users = {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User(**row)
            users[user.id] = user
    return users