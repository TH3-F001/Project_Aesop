class MissingArgumentException(Exception):
    def __init__(self, arg_name, errors=None):
        self.message = f"Requires missing argument: {arg_name}"
        super().__init__(self.message)
        self.errors = errors
