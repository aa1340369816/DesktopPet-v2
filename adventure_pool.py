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
                        "next": "end"
                    },
                    {
                        "text": texts.ADVENTURE_TEXTS["starscout"]["ch1"]["options"][1],
                        "effects": {
                            "set_flag": "starscout_名片搁置"
                        },
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
                        "next": "end"
                    }
                ]
            }
        }
    }
]
