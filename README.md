# Humble_Bundles_Spider | Humble慈善包爬虫
A simple script for crawling the bundles currently on sale on Humble|一个简单爬取Humble Bundles当前在售的游戏慈善包脚本

# Usage  
Run the script through the command line:  `python3 app.py`, Wait for the script to finish. Final Results will be saved in a file which name like `now_sale_game_bundle_2025_09_25_17_37_50.json`, default path is `./spider_result/`

# Requirements  
- Python3
- requests
- json
- os
- time
- logging

# Note  
Result Json Style Like:
```
{
    "LEGO Worlds Collide 2025": {                                                   # Bundle Name
                                "game_nums": 16,                                    # Bundle Game Count
                                "start_sale_time": "2025-09-03T18:00:00",           # Bundle Start Sale Time
                                "end_sale_time": "2025-10-02T01:00:00",             # Bundle End Sale Time
                                "game_list": {
                                                "116.53": [                         # Price Level's Game List
                                                            {
                                                                "name": "LEGO® DC Super-Villains DELUXE EDITION",   
                                                                "platforms": "steam",       # Game Active Platform
                                                                "min_price_cny": 116.53,    # Game Price Level
                                                                "pic_url": "https://hb.imgi....."   # Game Cover Image
                                                            },
                                                            {
                                                                "name": "LEGO® Marvel Super Heroes 2 DELUXE EDITION",
                                                                "platforms": "steam",
                                                                "min_price_cny": 116.53,
                                                                "pic_url": "https://hb.imgi....."
                                                            },
                                                            ...
                                                        ],
                                                "77.69": [....],
                                                .....,
                                            },
                                "cover_image_url": "https://hb.imgix.net/e88...."   # Bundle Cover Image
                                }
    "Lone Survivor Bundle":{......},
    ....

}
```
