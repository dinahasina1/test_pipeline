import httpx
from typing import List


class WebhookClient:
    def __init__(self, url: str):
        self.url = url

    def send_sample(self, sample: List) -> None:
        with httpx.Client() as client:
            client.post(self.url, json=[p.model_dump(mode="json") for p in sample])
