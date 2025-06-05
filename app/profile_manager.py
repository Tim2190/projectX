import json
import os
from typing import Dict, Optional

PROFILES_PATH = os.path.join(os.path.dirname(__file__), '..', 'profiles', 'profiles.json')

class ProfileManager:
    def __init__(self):
        os.makedirs(os.path.dirname(PROFILES_PATH), exist_ok=True)
        if not os.path.exists(PROFILES_PATH):
            with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def load_profiles(self) -> Dict[str, Dict[str, str]]:
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_profiles(self, profiles: Dict[str, Dict[str, str]]):
        with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)

    def get_profile(self, name: str) -> Optional[Dict[str, str]]:
        return self.load_profiles().get(name)

    def add_profile(self, name: str, keys: Dict[str, str]):
        profiles = self.load_profiles()
        profiles[name] = keys
        self.save_profiles(profiles)
