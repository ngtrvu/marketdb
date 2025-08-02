from dataclasses import dataclass


@dataclass
class VCAMConfig:
    api_token: str
    access_code: str
    host: str = ""
    url: str = f"https://{host}" if host else ""
    app_version: str = "1.2.0"
    app_locale: str = "vi"
    app_name: str = "STAG"
