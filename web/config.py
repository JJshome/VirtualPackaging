"""Configuration for the VirtualPackaging web interface."""

import os
from typing import List


class WebConfig:
    """Web application configuration."""
    # Server settings
    HOST = os.getenv("WEB_HOST", "0.0.0.0")
    PORT = int(os.getenv("WEB_PORT", "8000"))
    DEBUG = os.getenv("WEB_DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # Static file settings
    STATIC_DIR = os.getenv("STATIC_DIR", "static")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    
    # Frontend settings
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Authentication settings
    AUTH_ENABLED = os.getenv("AUTH_ENABLED", "False").lower() == "true"
    JWT_SECRET = os.getenv("JWT_SECRET", "development_secret_key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    # API settings
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    API_VERSION = os.getenv("API_VERSION", "v1")
    
    # Feature flags
    ENABLE_LLM = os.getenv("ENABLE_LLM", "True").lower() == "true"
    ENABLE_COST_ESTIMATION = os.getenv("ENABLE_COST_ESTIMATION", "True").lower() == "true"
    ENABLE_EXPORT = os.getenv("ENABLE_EXPORT", "True").lower() == "true"