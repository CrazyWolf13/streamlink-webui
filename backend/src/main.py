from fastapi import FastAPI
from frontend_app import frontend_app
from api_app import api_app

app = FastAPI()

# Mount the API app at /api/v1
app.mount("/api/v1", api_app, name="api")


# Mount the frontend app at the root
app.mount("/", frontend_app, name="frontend")

