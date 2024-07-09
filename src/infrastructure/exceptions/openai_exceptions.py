class OpenAIRateLimitExceededException(Exception):
    def __init__(self, message="ChatGPT Rate limit exceeded", errors=None):
        super().__init__(message)
        self.errors = errors

class OpenAITokenLengthExceededException(Exception):
    def __init__(self, message="The token length of this chatgpt session has been exceeded. Consider clearing the history or creating a new ChatGPTCompletionsRequest", errors=None):
        super().__init__(message)
        self.errors = errors

class OpenAIContentFilterException(Exception):
    def __init__(self, message="Your request triggered OpenAI's content filter. Try being less based.", errors=None):
        super().__init__(message)
        self.errors = errors

class OpenAIUnexpectedFinishReason(Exception):
    def __init__(self, message="OpenAI Request returned with an unkown finish reason", errors=None):
        super().__init__(message)
        self.errors = errors
