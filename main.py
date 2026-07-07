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
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
import yaml
import os

app = FastAPI()

# CORS: lets a browser on ANY website call this API directly.
# Without this, the grader's page would be blocked by the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Layer 1: hardcoded defaults ----
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# ---- Layer 2: the YAML file ----
def load_yaml_layer():
    env_name = os.getenv("APP_ENV", "development")
    filename = f"config.{env_name}.yaml"
    if os.path.exists(filename):
        with open(filename) as f:
            return yaml.safe_load(f) or {}
    return {}

# ---- Layer 3: the .env FILE (not the real OS environment) ----
def load_dotenv_layer():
    # dotenv_values reads the file into a dict WITHOUT touching
    # os.environ, so it can never be confused with real OS env vars.
    values = dotenv_values(".env")
    layer = {}
    for key, val in values.items():
        if val is None:
            continue
        if key == "NUM_WORKERS":          # the special alias
            layer["workers"] = val
        elif key.startswith("APP_"):
            layer[key[len("APP_"):].lower()] = val
    return layer

# ---- Layer 4: real OS-level environment variables ----
def load_os_env_layer():
    layer = {}
    for key, val in os.environ.items():
        if key.startswith("APP_"):
            layer[key[len("APP_"):].lower()] = val
    return layer

# ---- Turn everything into the right type ----
def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)

@app.get("/effective-config")
def effective_config(request: Request):
    # Merge low → high precedence, each step overwriting the last
    config = dict(DEFAULTS)
    config.update(load_yaml_layer())
    config.update(load_dotenv_layer())
    config.update(load_os_env_layer())

    # ---- Layer 5: CLI overrides via ?set=key=value ----
    for item in request.query_params.getlist("set"):
        if "=" in item:
            k, v = item.split("=", 1)
            config[k.strip()] = v.strip()

    result = {
        key: coerce(key, config.get(key))
        for key in ("port", "workers", "debug", "log_level", "api_key")
    }
    result["api_key"] = "****"   # always mask, no matter what
    return result

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8008)


