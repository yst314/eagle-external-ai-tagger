import dataclasses
import argparse
import requests
import json
from urllib.parse import urljoin

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://localhost:41595/")
    return parser.parse_args()

API = {
    # Application endpoints
    "APPLICAION_INFO" : "api/application/info",
    # Folder endpoints
    "FOLDER_CREATE" : "/api/folder/create",
    "FOLDER_RENAME" : "/api/folder/rename",
    "FOLDER_UPDATE" : "/api/folder/update",
    "FOLDER_LIST" : "/api/folder/list",
    "FOLDER_LIST_RECENT" : "/api/folder/listRecent",
    # Item endpoints
    "ITEM_ADD_FROM_URL" : "/api/item/addFromURL",
    "ITEM_ADD_FROM_URLS" : "/api/item/addFromURLs",
    "ITEM_ADD_FROM_PATH" : "/api/item/addFromPath",
    "ITEM_ADD_FROM_PATHS" : "/api/item/addFromPaths",
    "ITEM_ADD_BOOKMARK" : "/api/item/addBookmark",
    "ITEM_INFO" : "/api/item/info",
    "ITEM_THUMBNAIL" : "/api/item/thumbnail",
    "ITEM_LIST" : "/api/item/list",
    "ITEM_MOVE_TO_TRASH" : "/api/item/moveToTrash",
    "ITEM_REFRESH_PALETTE" : "/api/item/refreshPalette",
    "ITEM_REFRESH_THUMBNAIL" : "/api/item/refreshThumbnail",
    "ITEM_UPDATE" : "/api/item/update",
    # Library endpoints
    "LIBRARY_INFO" : "/api/library/info",
    "LIBRARY_HISTORY" : "/api/library/history",
    "LIBRARY_SWITCH" : "/api/library/switch",
    "LIBRARY_ICON" : "/api/library/icon"
}

def get_api_path(name):
    try:
        return API[name]
    except Exception as e:
        print(f"No name of api: {name}")
        raise e
    
class EagleApi:
    def __init__(self, eagle_url="http://localhost:41595/"):
        self.eagle_url = eagle_url
    
    def _combine_url(self, api_path):
        eagle_url = self.eagle_url.rstrip('/')
        api_path = api_path.lstrip('/')
        return urljoin(f"{eagle_url}/", api_path)

    def _create_post_request_options(self, data):
        return {
        "method": 'POST',
        "headers": {
            'Content-Type': 'application/json'
        },
        "body": json.dumps(data),
        "redirect": 'follow'
        }
    
    def _parse_response(self, response:requests.Response):
        try:
            if response.status_code == 200:
                return response.json()["data"]
            else:
                raise requests.ConnectionError
        except Exception as e:
            print("STATUS CODE: ", response.status_code, response.reason)

    def item_info(self, item_id):
        request_url = self._combine_url(get_api_path("ITEM_INFO"))
        request_url = request_url + f"?id={item_id}"
        return self._parse_response(requests.get(request_url))

    def item_list(self, limit=200, offset=0, order_by="CREATEDATE"):
        request_url = self._combine_url(get_api_path("ITEM_LIST"))
        request_url = request_url + f"?limit={limit}&offset={offset}&orderBy={order_by}"
        return self._parse_response(requests.get(request_url))

    def library_info(self):
        request_url = self._combine_url(get_api_path("LIBRARY_INFO"))
        return self._parse_response(requests.get(request_url))

    def aplication_info(self):
        request_url = self._combine_url(get_api_path("APPLICAION_INFO"))
        return self._parse_response(requests.get(request_url))

    def item_update(self, data):
        # request_options = self._create_post_request_options(data)
        request_url = self._combine_url(get_api_path("ITEM_UPDATE"))
        return self._parse_response(requests.post(request_url, json=data))

def all_item_list_generator(eagle_url="http://localhost:41595/", limit=200):
    ea = EagleApi(eagle_url)
    offset = 0
    while True:
        result = ea.item_list(limit=limit, offset=offset)
        if len(result) == 0:
            break
        for data in result:
            yield data
        offset += 1

if __name__ == "__main__":
    from predictor import Predictor
    args = parse_args()

    ea = EagleApi(eagle_url=args.url)
    # result = ea.item_list(offset=4)
    # print(result)
    item = next(all_item_list_generator(limit=1000))

    # Predictor()
    print(item)

    data = {
        "id": item["id"],
        "tags": item["tags"],
        # "annotation": item["annotation"],
        # "url": item["url"],
        # "star": 5
    }
    # result = ea.item_update(data)
    