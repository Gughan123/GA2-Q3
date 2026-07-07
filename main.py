"""from fastapi import FastAPI
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
    }"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def load_yaml(path) -> dict:
    res = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    res[k.strip()] = v.strip().strip('"').strip("'")
    return res


def load_dotenv(path) -> dict:
    res = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    res[k.strip()] = v.strip().strip('"').strip("'")
    return res


@app.get("/effective-config")
def get_config(request: Request):
    cfg = DEFAULTS.copy()

    y = load_yaml("config.development.yaml")
    cfg.update({k: y[k] for k in cfg if k in y})

    dotenv = load_dotenv(".env")
    mappings = {
        "APP_PORT": "port",
        "NUM_WORKERS": "workers",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for env_k, cfg_k in mappings.items():
        if env_k in dotenv:
            cfg[cfg_k] = dotenv[env_k]
        if env_k in os.environ:
            cfg[cfg_k] = os.environ[env_k]

    for param_name, param_val in request.query_params.multi_items():
        if param_name == "set" and "=" in param_val:
            k, v = param_val.split("=", 1)
            k = "workers" if k.strip() == "NUM_WORKERS" else k.strip()
            if k in cfg:
                cfg[k] = v

    return {
        "port": int(cfg["port"]),
        "workers": int(cfg["workers"]),
        "debug": str(cfg["debug"]).lower() in {"true", "1", "yes", "on"},
        "log_level": str(cfg["log_level"]),
        "api_key": "******",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8008)

@app.get("/debug-env")
def debug_env():
    return {
        "APP_PORT": os.environ.get("APP_PORT"),
        "APP_DEBUG": os.environ.get("APP_DEBUG"),
    }
