class AppError(Exception):
    def __init__(self, message: str = "", payload=None):
        self.message = f"Error: {str(message)}"
        self.payload = payload

    def __str__(self):
        return self.message
