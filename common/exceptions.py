class RateLimitExceededException(Exception):
    def __init__(self, message="ChatGPT Rate limit exceeded", errors=None):
        super().__init__(message)
        self.errors = errors
