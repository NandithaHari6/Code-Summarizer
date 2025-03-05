import time
import threading
import tiktoken

# Load the tokenizer (cl100k_base is used in GPT-4, similar to LLaMA)







class APIKeyManager:
    def __init__(self, api_keys, max_tokens_per_minute=6000, max_tokens_per_day=100000, 
                 max_requests_per_minute=30, max_requests_per_day=1000):
        self.api_keys = api_keys
        self.token_usage = {key: 0 for key in api_keys}
        self.request_count = {key: 0 for key in api_keys}

        self.token_usage_day = {key: 0 for key in api_keys}
        self.request_count_day = {key: 0 for key in api_keys}
        self.lock = threading.Lock()
        self.current_index = 0
        self.last_minute_reset = time.time()
        self.last_day_reset = time.time()
        self.reset_minute_interval = 60  # 1 min
        self.reset_day_interval = 86400  # 24 hours
        self.max_tokens_per_minute = max_tokens_per_minute
        self.max_tokens_per_day = max_tokens_per_day
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_day = max_requests_per_day
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    def _reset_limits(self):
        """Resets request and token counts when limits reset."""
        with self.lock:
            current_time = time.time()
            if current_time - self.last_minute_reset >= self.reset_minute_interval:
                for key in self.api_keys:
                    self.token_usage[key] = 0
                    self.request_count[key] = 0
                self.last_minute_reset = current_time

            if current_time - self.last_day_reset >= self.reset_day_interval:
                for key in self.api_keys:
                    self.token_usage_day[key] = 0
                    self.request_count_day[key] = 0
                self.last_day_reset = current_time
    def count_tokens(self,prompt):
   
        return len(self.tokenizer.encode(prompt))

    def get_available_key(self,prompt):
        tokens_needed=self.count_tokens(prompt)
        """Returns an API key that can process the request or waits until one is available."""
        while True:
            self._reset_limits()
            with self.lock:
                for i in range(len(self.api_keys)):
                    key = self.api_keys[self.current_index]
                    if (self.token_usage[key] + tokens_needed <= self.max_tokens_per_minute and
                        sum(self.token_usage.values()) + tokens_needed <= self.max_tokens_per_day and
                        self.request_count[key] < self.max_requests_per_minute and
                        sum(self.request_count.values()) < self.max_requests_per_day):
                        
                        self.token_usage[key] += tokens_needed
                        self.request_count[key] += 1
                        self.current_index = (self.current_index + 1) % len(self.api_keys)
                        return key
                
            time.sleep(1)  # Wait for the next reset if all keys are exhausted

