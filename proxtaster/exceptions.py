class TooManyOpenFilesError(Exception):
    def __init__(self, message: str, previous: Exception):
        super().__init__(message)
        self.previous = previous

    def getPrevious() -> Exception:
        return self.previous
