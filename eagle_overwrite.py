import os 
import argparse
import json 
from glob import glob

from tqdm import tqdm
from PIL import Image

from predictor import Predictor
from api import EagleApi, all_item_list_generator

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("library_path", type=str)
    parser.add_argument("--eagle_url", type=str, default="http://localhost:41595")
    parser.add_argument("--model-repo", type=str, default="SmilingWolf/wd-swinv2-tagger-v3")
    parser.add_argument("--general-thresh", type=float, default=0.35)
    parser.add_argument("--general-mcut-enabled", action="store_true")
    parser.add_argument("--character-thresh", type=float, default=0.85)
    parser.add_argument("--character-mcut-enabled", action="store_true")

    return parser.parse_args()

def main():
    args = parse_args()

    library_path = args.library_path
    eagle_url = args.eagle_url

    model_repo = args.model_repo
    general_thresh = args.general_thresh
    general_mcut_enabled = args.general_mcut_enabled
    character_thresh = args.character_thresh
    character_mcut_enabled = args.character_mcut_enabled
    images_path = os.path.join(library_path, "images")

    ea = EagleApi(eagle_url)
    predictor = Predictor()

    for item in tqdm(all_item_list_generator(eagle_url=eagle_url)):
        if ":AutoTagged" in item["tags"]:
            continue
        item_dir = os.path.join(images_path, item["id"]+".info")
        if item["ext"] in ["jpg", "png", "webp"]:
            image_path = os.path.join(item_dir, f"{item['name']}.{item['ext']}")
        else:
            thumbnail_name = glob(os.path.join(item_dir, "*_thumbnail.png"))
            if len(thumbnail_name):
                image_path = os.path.join(item_dir, thumbnail_name[0])
            else:
                continue
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
        
        data = {
            "id": item["id"],
            "tags": item["tags"] + tags
        }
        ea.item_update(data)
if __name__ == "__main__":
    main()