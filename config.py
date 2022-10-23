import os


class Config:
    """Service configurations"""
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8000"))