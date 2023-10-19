import os
from dataclasses import dataclass


@dataclass
class Environment:
    port: int
    secret_key: str
    client_id: str
    client_secret: str
    host_url: str
    allowed_domains: str
    allowed_addresses: str
    database_url: str
    use_flask_debug_mode: bool

    @classmethod
    def from_env(cls) -> "Environment":
        return cls(
            port=int(os.environ.get("PORT", 8080)),
            secret_key=cls.require_env("SECRET_KEY"),
            client_id=cls.require_env("CLIENT_ID"),
            client_secret=cls.require_env("CLIENT_SECRET"),
            host_url=cls.require_env("HOST_URL"),
            allowed_domains=os.environ.get("ALLOWED_DOMAINS", ""),
            allowed_addresses=os.environ.get("ALLOWED_ADDRESSES", ""),
            database_url=cls.require_env("DATABASE_URL"),
            use_flask_debug_mode=os.environ.get("USE_FLASK_DEBUG_MODE", "true")
            == "true",
        )

    @classmethod
    def require_env(cls, name: str) -> str:
        value = os.environ.get(name)
        if value is None:
            raise Exception(f"Unable to read {name} from the environment")
        return value
