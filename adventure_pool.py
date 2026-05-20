# adventure_pool.py
import adventure_texts as texts

ADVENTURES = [
    {
        "id": "starscout",
        "name": "星探的凝视",
        "category": "职业入口",
        "desc": "一个穿深灰色风衣的男人在便利店注意到了你。",
        "location": "便利店",
        "trigger": {
            "charm_min": 28,
            "activity": "便利店兼职",
            "activity_count_min": 3
        },
        "base_probability": 0.3,
        "stages": {
            "ch1": {
                "text": texts.ADVENTURE_TEXTS["starscout"]["ch1"]["text"],
                "location": "便利店收银台",
                "options": [
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch1"]["options"][0],
                        "effects": {
                            "mood": 5,
                            "set_flag": "starscout_名片入包",
                            "give_item": {
                                "id": "starscout_card",
                                "name": "星探名片",
                                "desc": "姜民赫的名片。星娱公司新人开发部。他说——想好了随时联系。",
                                "usable": True
                            }
                        },
                        "result": "你打开手机，输入“姜民赫 星娱”。搜索结果第一条就是他的采访——星娱十二年老牌星探，挖掘过三支出道组合。不是骗子。你深吸一口气，把名片收进背包最里面的夹层。",
                        "next": "end"
                    },
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch1"]["options"][1],
                        "effects": {
                            "set_flag": "starscout_名片搁置"
                        },
                        "result": "你把名片放在收银台抽屉里，没扔，但也没带回家。下班时你看了眼那个抽屉，犹豫了一下，还是关上了。名片还在那儿。",
                        "next": "end"
                    }
                ]
            },
            "ch1_variant": {
                "text": texts.ADVENTURE_TEXTS["starscout"]["ch1_variant"]["text"],
                "location": "便利店收银台",
                "stage_trigger": {
                    "activity": "便利店兼职",
                    "flag_required": ["starscout_名片搁置"]
                },
                "options": [
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch1_variant"]["options"][0],
                        "effects": {
                            "remove_flag": "starscout_名片搁置",
                            "set_flag": "starscout_名片入包",
                            "give_item": {
                                "id": "starscout_card",
                                "name": "星探名片",
                                "desc": "姜民赫的名片。星娱公司新人开发部。他说——想好了随时联系。",
                                "usable": True
                            }
                        },
                        "result": "你把名片从抽屉里拿出来，轻轻吹掉上面的灰尘。这一次，你决定不再把它丢下了。名片被小心地放进了背包最里面的夹层。",
                        "next": "end"
                    }
                ]
            },
            "ch2": {
                "text": texts.ADVENTURE_TEXTS["starscout"]["ch2"]["text"],
                "location": "家中",
                "stage_trigger": {
                    "trigger_type": "item_use",
                    "item_id": "starscout_card",
                    "flag_required": ["starscout_名片入包"]
                },
                "options": [
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch2"]["options"][0],
                        "effects": {
                            "update_item_desc": {
                                "id": "starscout_card",
                                "desc": "面试定在30分钟后。星娱大楼十一层。报姜民赫的名字。"
                            },
                            "set_timer": 30,
                            "set_flag": "starscout_等待面试"
                        },
                        "result": "你记下了面试信息。挂断电话后，手心微微出汗。30分钟后，星娱大楼十一层，报姜民赫的名字。",
                        "next": "end"
                    }
                ]
            },
            "ch3": {
                "text": texts.ADVENTURE_TEXTS["starscout"]["ch3"]["text"],
                "location": "星娱大楼十一层等候区",
                "stage_trigger": {
                    "trigger_type": "timer",
                    "flag_required": ["starscout_等待面试"]
                },
                "options": [
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch3"]["options"][0],
                        "effects": {
                            "trait_add": "星探发掘",
                            "give_item": {
                                "id": "mint_candy",
                                "name": "薄荷糖",
                                "desc": "一颗普通的薄荷糖。他说面试前都吃这个，算是个仪式。",
                                "usable": False
                            },
                            "update_item_desc": {
                                "id": "starscout_card",
                                "desc": "姜民赫的名片。他写在背面的字——「不管今天结果如何，你已经比大多数人勇敢了。」"
                            },
                            "remove_flag": "starscout_等待面试"
                        },
                        "result": "你接过薄荷糖，凉意冲散了紧张。你坐在长椅上，等着自己的号码被叫到。姜民赫的名片在口袋里微微发烫。",
                        "next": "end"
                    }
                ]
            }
        }
    }
]
