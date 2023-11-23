class OfferProcessingError(Exception):
    """Exception raised for errors in processing offer URLs."""

    def __init__(self, url, message="Error processing offer URL"):
        self.url = url
        self.message = f"{message}: {url}"
        super().__init__(self.message)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"
