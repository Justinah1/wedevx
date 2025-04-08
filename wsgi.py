from main import app
import uvicorn

# This is a special module that provides a WSGI-compatible interface for gunicorn
# by wrapping the FastAPI ASGI application
from uvicorn.workers import UvicornWorker

class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "asyncio", "http": "h11", "lifespan": "off"}