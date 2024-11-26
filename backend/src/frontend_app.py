from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

frontend_app = FastAPI()

# Mount static frontend files
frontend_app.mount("/", StaticFiles(directory="../../frontend/src/dist", html=True), name="static")


