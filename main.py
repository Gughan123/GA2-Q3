from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)
@app.get("/")
def home():
    return {"message": "Hello FastAPI!"}

@app.get("/effective-config")
def effective_config():
    return {
        "port": 8591,
        "workers": 4,
        "debug": False,
        "log_level": "info",
        "api_key": "****"
    }
