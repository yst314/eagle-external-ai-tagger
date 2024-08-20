import os 
import argparse
import json 
from glob import glob

from tqdm import tqdm
from PIL import Image

from predictor import Predictor

# Dataset v3 series of models:
# SWINV2_MODEL_DSV3_REPO = "SmilingWolf/wd-swinv2-tagger-v3"
# CONV_MODEL_DSV3_REPO = "SmilingWolf/wd-convnext-tagger-v3"
# VIT_MODEL_DSV3_REPO = "SmilingWolf/wd-vit-tagger-v3"
# VIT_LARGE_MODEL_DSV3_REPO = "SmilingWolf/wd-vit-large-tagger-v3"
# EVA02_LARGE_MODEL_DSV3_REPO = "SmilingWolf/wd-eva02-large-tagger-v3"
def append_eagle_tags(json_path, tags):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    [data["tags"].append(tag) for tag in tags if not tag in data["tags"]]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("library_path", type=str)
    parser.add_argument("--model-repo", type=str, default="SmilingWolf/wd-swinv2-tagger-v3")
    parser.add_argument("--general-thresh", type=float, default=0.35)
    parser.add_argument("--general-mcut-enabled", action="store_true")
    parser.add_argument("--character-thresh", type=float, default=0.85)
    parser.add_argument("--character-mcut-enabled", action="store_true")

    return parser.parse_args()

def main():
    args = parse_args()

    model_repo = args.model_repo

    general_thresh = args.general_thresh
    general_mcut_enabled = args.general_mcut_enabled
    character_thresh = args.character_thresh
    character_mcut_enabled = args.character_mcut_enabled
    library_path = args.library_path
    images_path = os.path.join(library_path, "images")
    image_dirs = glob(os.path.join(images_path, "*.info"))

    predictor = Predictor()

    for image_dir in tqdm(image_dirs):
        image_path = glob(os.path.join(image_dir, "*.jpg")) + glob(os.path.join(image_dir, "*.png"))
        json_path = glob(os.path.join(image_dir, "*.json"))
        if not len(image_path) or not len(json_path):
            continue
        image_path = image_path[0]
        json_path = json_path[0]
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
        if not character_res == {}:
            tags += list(character_res.keys())
        tags.append(rating)

        tags = [tag + " :Auto" for tag in tags]

        tags.append(":AutoTagged")
        append_eagle_tags(json_path, tags)

if __name__ == "__main__":
    main()