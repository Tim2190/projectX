import json
import os
from typing import List, Dict

SOURCES_PATH = os.path.join(os.path.dirname(__file__), '..', 'profiles', 'sources.json')

class SourceManager:
    def __init__(self, path: str = SOURCES_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_sources(self) -> List[Dict[str, str]]:
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_sources(self, sources: List[Dict[str, str]]):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
