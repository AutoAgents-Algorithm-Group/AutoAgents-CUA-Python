class CaptchaConfig:
    model: str
    base_url: str
    api_key: str

    def __init__(self, model: str, base_url: str, api_key: str):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key