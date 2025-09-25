
import os
import time
import json
import requests
import logging
from logging.handlers import RotatingFileHandler

# Logging Utils
APP_LOG = logging.getLogger(__name__)
log_file = f"app_log_{time.strftime('%Y_%m_%d', time.localtime())}.log"
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = RotatingFileHandler(log_file, maxBytes=2*1024*1024, backupCount=5,encoding="utf-8")
file_handler.setFormatter(formatter)
APP_LOG.addHandler(file_handler)
APP_LOG.addHandler(logging.StreamHandler())
APP_LOG.setLevel(logging.INFO)



def get_website_str(url:str):
    '''
    Sends a GET request to the specified URL and returns the response as a string.
    Parameters:
        url (str): The URL to send the GET request to.

    Returns:
        str: The response from the server as a string.

    Example:
        >>> get_website_str('https://www.example.com')
        '<html>...</html>'
    '''
    try:
        response = requests.get(url, timeout=30)
    except Exception as e:
        APP_LOG.error(f"Url Get Error, URL:{url} , Error Message:{e}")
        exit(-1)
    return response.text

def probe_json_from_str(json_str:str):
    '''
    Parses a JSON string and returns a dictionary containing the parsed JSON data.
    Parameters:
        json_str (str): The JSON string to parse.

    Returns:
        dict: A dictionary containing the parsed JSON data.

    Example:
        >>> probe_json_from_str('{"name": "John", "age": 30}')
        {'name': 'John', 'age': 30}
    '''
    try:
        return json.loads(json_str)
    except Exception as e:
        APP_LOG.error(f"[ERROR] Json Parse Error, Json:{json_str} , Error Message:[{e}]")
        exit(-1)

def write_json_to_file(json_data:dict, file_path:str):
    '''
    Writes a JSON object to a file.
    Parameters:
        json_data (dict): The JSON object to write to the file.
        file_path (str): The path to the file to write to.

    Returns:
        None

    Example:
        >>> write_json_to_file({"name": "John", "age": 30}, "data.json")
    '''
    try:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        APP_LOG.info(f"[RESULT] Result Json Write Success, See the file:[{file_path}] for more details")
    except Exception as e:
        APP_LOG.error(f"Json Write Error, File Path:[{file_path}], Json:{json_data}, Error Message:[{e}]")
        exit(-1)
    

def main(humble_url:str):
    '''
    The main function of the program.
    '''
    APP_LOG.info("[INFO] Starting...")
    now_sale_game_bundle_dict = {}

    humble_bundles_page_str = get_website_str(humble_url)
    APP_LOG.info("[INFO] Get Humble Bundles Page String Success")
    bundles_info_json_str = humble_bundles_page_str.split("landingPage-json-data")[-1].replace('''" type="application/json">\n ''',"").split("\n</script>")[0]
    bundles_info_json_data = probe_json_from_str(bundles_info_json_str)
    bundles_info_json = bundles_info_json_data["data"]["games"]["mosaic"][0]["products"]
    APP_LOG.info("[INFO] Start Getting Bundle Info...")
    for bundle_info in bundles_info_json:
        bundle_name = bundle_info["tile_short_name"]
        bundle_start_sale_time = bundle_info["start_date|datetime"]
        bundle_end_sale_time = bundle_info["end_date|datetime"]
        bundle_cover_image_url = bundle_info["tile_image"]
        bundle_info_website_url = "https://www.humblebundle.com"+ bundle_info["product_url"]
        APP_LOG.info(f"[INFO] Found Bundle:[{bundle_name}, Processing...")

        bundle_info_page_str = get_website_str(bundle_info_website_url)
        bundle_info_json_str = bundle_info_page_str.split("webpack-bundle-page-data")[-1].replace('''" type="application/json">\n  ''',"").split("\n</script>")[0]
        bundle_info_json = probe_json_from_str(bundle_info_json_str)

        now_exchage_rate_dict = bundle_info_json["exchangeRates"]      # Now Exchange Rate

        # NOTICE: If you did not in China or USA, you need to change the exchange rate to your country's exchange rate.
        now_CNY_exchage_rate = now_exchage_rate_dict.get("CNY|decimal")
        is_CNY_mode = bundle_info_json["ipInChina"]     # HumbleBundle through this flag to know whether you are in China or not.
        
        level_money_dict = {}   # Record the price of each level
        for level_price in bundle_info_json["bundleData"]["preset_prices"]:
            if is_CNY_mode:
                now_level_price_CNY = round(level_price["price|money"]["amount"], 2)
            else:
                now_level_price_CNY = round((level_price["price|money"]["amount"] * now_CNY_exchage_rate), 2)
            
            now_level = level_price["qualifying_tier_id"]
            if now_level not in level_money_dict:
                level_money_dict[now_level] = [now_level_price_CNY]
            else:
                level_money_dict[now_level].append(now_level_price_CNY)
        
        all_game_info = bundle_info_json["bundleData"]["tier_item_data"]
        
        level_game_dict = {}
        game_num = 0
        for game_info in all_game_info:
            game_name = all_game_info[game_info]["human_name"]
            if all_game_info[game_info].get("min_price|money") is None:
                APP_LOG.debug(f"[RESULT] Bundle:[{bundle_name}], there is a game: [{game_name}], has no min price info, maybe is an organization, Skip Record.")
                continue
            
            if is_CNY_mode:
                game_min_price_cny = round(all_game_info[game_info]["min_price|money"]["amount"], 2)
            else:
                game_min_price_cny = round((all_game_info[game_info]["min_price|money"]["amount"] * now_CNY_exchage_rate), 2)
            
            game_pic_url = all_game_info[game_info]["resolved_paths"]["featured_image"]
            game_activate_platform = list(all_game_info[game_info]["platforms_and_oses"]["game"].keys())[0]

            for price in level_money_dict:
                if game_min_price_cny in level_money_dict[price]:
                    game_num += 1
                    if game_min_price_cny not in level_game_dict:
                        level_game_dict[game_min_price_cny] = [{"name":game_name, "platforms":game_activate_platform, "min_price_cny":game_min_price_cny, "pic_url":game_pic_url}]
                    else:
                        level_game_dict[game_min_price_cny].append({"name":game_name, "platforms":game_activate_platform, "min_price_cny":game_min_price_cny, "pic_url":game_pic_url})

        now_sale_game_bundle_dict[bundle_name] = {"game_nums":game_num, "start_sale_time":bundle_start_sale_time, "end_sale_time":bundle_end_sale_time, "game_list":level_game_dict, "cover_image_url":bundle_cover_image_url}
        APP_LOG.info(f"[RESULT] Bundle:[{bundle_name}] Process Finish, There are [{game_num}] games in this bundle, price level is {list(level_game_dict.keys())}")
    
    return now_sale_game_bundle_dict


if __name__ == "__main__":
    now_sale_game_bundle_dict = main("https://www.humblebundle.com/games")
    # print(now_sale_game_bundle_dict)
    write_json_to_file(now_sale_game_bundle_dict, f"spider_result/now_sale_game_bundle_{time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())}.json")
    print("Finish")
        


            


            












