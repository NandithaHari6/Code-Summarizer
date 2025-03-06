from fastapi import FastAPI, HTTPException
import os
import time
import requests
app = FastAPI()

class LLMRateLimiter:
    def __init__(self, key_env_names, limits):
        """
        Initialize rate limiter with API keys loaded from environment variables.
        """

        self.api_keys = [
            {"index": i, "req_per_min": 0, "tok_per_min": 0, "req_per_day": 0, "tok_per_day": 0}
            for i in range(len(key_env_names))
        ]
        self.key_env_names = key_env_names  # Stores env variable names
        self.limits = limits
        self.last_minute_check = time.time()
        self.last_day_check = time.time()

    def reset_limits(self):
        """
        Reset per-minute and per-day counters when required.
        """
        current_time = time.time()

        if current_time - self.last_minute_check >= 60:
            for key in self.api_keys:
                key["req_per_min"] = 0
                key["tok_per_min"] = 0
            self.last_minute_check = current_time

        if current_time - self.last_day_check >= 86400:  # 24 hours
            for key in self.api_keys:
                key["req_per_day"] = 0
                key["tok_per_day"] = 0
            self.last_day_check = current_time

    def select_best_api_key(self):
        """
        Select the API key index with the most available capacity.
        """
        self.reset_limits()

        sorted_keys = sorted(
            self.api_keys,
            key=lambda k: min(
                self.limits["req_per_min"] - k["req_per_min"],
                self.limits["tok_per_min"] - k["tok_per_min"],
                self.limits["req_per_day"] - k["req_per_day"],
                self.limits["tok_per_day"] - k["tok_per_day"]
            ),
            reverse=True
        )

        for key in sorted_keys:
            if (
                key["req_per_min"] < self.limits["req_per_min"] and
                key["tok_per_min"] < self.limits["tok_per_min"] and
                key["req_per_day"] < self.limits["req_per_day"] and
                key["tok_per_day"] < self.limits["tok_per_day"]
            ):
                return key["index"]

        return None  # No available API key

    def update_usage(self, key_index, used_tokens):
        """
        Update token and request counters for the selected API key index.
        """
        for key in self.api_keys:
            if key["index"] == key_index:
                key["req_per_min"] += 1
                key["tok_per_min"] += used_tokens
                key["req_per_day"] += 1
                key["tok_per_day"] += used_tokens
                break







