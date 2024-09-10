# fastapi
from fastapi import FastAPI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from predictor import Predictor

class Settings(BaseSettings):
    app_name: str = "My FastAPI App"
    api_version: str = "1.0.0"
    debug: bool = False
    library_root: str = ""
    model_repo: str = ""
    model_config = ""
    # 他の設定値を追加可能
    class Config:
        env_file = ".env"

app = FastAPI()
settings = Settings()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/getSettings")
def get_settings():
    return settings.dict()

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

class Data(BaseModel):
    image_path: str
    model_repo: str
    general_thresh: float
    general_mcut_enabled: bool
    character_thresh: float
    character_mcut_enabled: bool

from PIL import Image
predictor = Predictor()

@app.get("/predict")
def predict(
    image_path: str,
    model_repo: str,
    general_thresh: float,
    general_mcut_enabled: bool,
    character_thresh: float,
    character_mcut_enabled: bool
):
    image = Image.open(image_path).convert("RGBA")
    sorted_general_strings, rating, character_res, general_res = predictor.predict(
        image,
        model_repo,
        general_thresh,
        general_mcut_enabled,
        character_thresh,
        character_mcut_enabled
    )
    
    rating = max(rating, key=rating.get)
    tags = sorted_general_strings.split(", ")
    
    if character_res:
        tags += list(character_res.keys())
        
    tags.append(rating)
    tags = [tag + " :Auto" for tag in tags]
    tags.append(":AutoTagged")
    
    return {"tags": tags}

