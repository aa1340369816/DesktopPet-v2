import random
import time
import tkinter as tk

# ==================== 事件数据池 ====================
EVENT_POOL = [
    # --------------------------------- Instant ---------------------------------
    {
        "id": "evt_store_001",
        "name": "过期便当的处理",
        "description": "今天是便当的保质期最后一天。店长说按规定要扔掉，但你看着那些完好的饭团和便当，觉得有点可惜。店长看你的表情，叹了口气说：'拿一盒走吧，剩下的必须扔。'",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"satiety": 5, "mood": 1},
        "toast": "不浪费食物，也是一种美德吧。",
        "cooldown": 600
    },
    {
        "id": "evt_store_002",
        "name": "夜班的寂静",
        "description": "凌晨三点，便利店里只有你和自动门偶尔发出的'叮咚'声。你擦了第三遍收银台，忽然觉得这个小小的空间像是城市里唯一亮着灯的孤岛。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 2, "fatigue": 3},
        "toast": "深夜的便利店，收留了很多不眠的人。",
        "cooldown": 600
    },
    {
        "id": "evt_store_003",
        "name": "常客的微笑",
        "description": "有一个大叔每天晚上都会来买同一款啤酒。今天他结账时多看了你一眼，说：'最近气色不错啊，年轻人。'你愣了一下，然后笑了。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 3, "charm": 1},
        "toast": "被陌生人注意到，是一种奇怪的温暖。",
        "cooldown": 600
    },
    {
        "id": "evt_store_004",
        "name": "盘点发现少了一包糖",
        "description": "你对着货架数了三遍，少了一包草莓味的棉花糖。你也不知道是自己数错了还是被偷了，最后还是自己掏钱补上了差额。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": -3, "mood": -1},
        "toast": "算了，就当请了一个隐形的小偷吃糖吧。",
        "cooldown": 600
    },
    {
        "id": "evt_store_005",
        "name": "学会了收银机的快捷操作",
        "description": "老员工教了你一个收银机的隐藏快捷方式，结账速度直接快了一倍。你觉得这个技能可能以后用不上，但学会新东西总是开心的。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 2, "gold": 3},
        "toast": "快捷键之神眷顾了你！",
        "cooldown": 600
    },
    {
        "id": "evt_store_006",
        "name": "搬货闪了腰",
        "description": "你逞强一个人搬了一箱饮料，结果腰上传来一阵酸痛。店长让你去休息室坐一会儿，嘴里念叨着'年轻人就是不知道珍惜身体'。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"stamina": -5, "sick": True, "fatigue": 5},
        "toast": "下次还是叫同事帮忙吧……",
        "cooldown": 600
    },
    {
        "id": "evt_store_007",
        "name": "遇到了以前的同学",
        "description": "一个高中同学走进来买东西，你在收银台后面和她四目相对。她惊讶地说：'你在这里上班？'你笑了笑说：'嗯，兼职。'她说：'挺好的，加油。'然后拿着东西走了。你看着她的背影，心情有点复杂。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 0, "popularity": 1},
        "toast": "被认出来了。没什么大不了的，对吧？",
        "cooldown": 600
    },
    {
        "id": "evt_store_008",
        "name": "收到小费",
        "description": "一位外国游客结账后把找零推回给你，用生硬的中文说'给你'。你想追出去还给他，但他已经走远了。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": 8, "mood": 2},
        "toast": "来自陌生人的善意。",
        "cooldown": 600
    },
    {
        "id": "evt_store_009",
        "name": "空调坏了的一天",
        "description": "便利店的空调在盛夏的中午坏了。你在收银台后面汗流浃背，感觉自己像一根正在融化的雪糕。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"hygiene": -3, "fatigue": 5, "mood": -3},
        "toast": "汗水带走了今天的力气。",
        "cooldown": 600
    },
    {
        "id": "evt_store_010",
        "name": "失物招领",
        "description": "你在货架间捡到一个钱包，里面有身份证和不少现金。你把它交给了店长。三天后失主回来取，给你买了一大袋水果表示感谢。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 4, "popularity": 2},
        "toast": "拾金不昧的感觉真好。",
        "cooldown": 600
    },
    {
        "id": "evt_store_011",
        "name": "店长请喝饮料",
        "description": "今天气温飙升，店长从冷柜里拿了一瓶运动饮料给你：'喝吧，算我的。'你接过来的时候瓶身冰凉，心里却暖了一下。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"stamina": 3, "mood": 2},
        "toast": "免费的饮料最好喝。",
        "cooldown": 600
    },
    {
        "id": "evt_store_012",
        "name": "货架摆放的艺术",
        "description": "你花了一个小时把膨化食品区摆得整整齐齐，颜色从浅到深渐变。店长看到后愣了三秒，说：'你是不是有强迫症？'但也没让你改回去。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 3, "charm": 1},
        "toast": "渐变色薯片架，今日最佳。",
        "cooldown": 600
    },
    {
        "id": "evt_store_013",
        "name": "深夜的奇怪顾客",
        "description": "凌晨两点，一个穿着睡衣的女生走进来，买了一盒冰淇淋、一包薯片和一瓶可乐。你帮她结账时她叹了口气说：'今天和男朋友分手了。'你不知道该说什么，默默多给了一个塑料袋。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1, "popularity": 1},
        "toast": "便利店是深夜伤心人的收容所。",
        "cooldown": 600
    },
    {
        "id": "evt_store_014",
        "name": "自动门故障",
        "description": "自动门像抽风一样开开合合，没人进出也响个不停。你用拖把杆敲了一下感应器，它居然好了。店长露出了不可思议的表情。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 2},
        "toast": "修理之道：敲就完了。",
        "cooldown": 600
    },
    {
        "id": "evt_store_015",
        "name": "被小朋友叫'阿姨/叔叔'",
        "description": "一个小朋友在店里大声喊：'阿姨/叔叔，这个多少钱？'你微笑着回答了他，然后在心里默默流泪。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": -1, "charm": 1},
        "toast": "我还没那么老吧……",
        "cooldown": 600
    },
    {
        "id": "evt_store_016",
        "name": "帮忙看管宠物",
        "description": "一位顾客把小狗拴在店门口，请你帮忙看两分钟。你在收银台后面和那只小狗对视了整整一百二十秒，它是你今天最好的同事。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 3},
        "toast": "小狗不会说话，但它的眼睛说了很多。",
        "cooldown": 600
    },
    {
        "id": "evt_store_017",
        "name": "关东煮的最后一个丸子",
        "description": "关东煮锅里只剩下最后一个竹轮卷。你和另一个同事同时看向它，然后同时笑了。最后你让给了他。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1, "popularity": 1},
        "toast": "让出去的丸子，收获的好感。",
        "cooldown": 600
    },
    {
        "id": "evt_store_018",
        "name": "夜班后的日出",
        "description": "你值完夜班走出店门，正好赶上日出。便利店在晨光里看起来和深夜完全不一样。你想，这个城市终于醒了，而你要去睡了。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 4, "fatigue": -2},
        "toast": "见过凌晨的便利店，也见过最早的日出。",
        "cooldown": 600
    },
    {
        "id": "evt_store_019",
        "name": "被夸奖服务态度",
        "description": "一位阿姨结账时忽然说：'你态度真好，我去了那么多家店，就你每次都会笑着说欢迎光临。'",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 4, "charm": 2, "popularity": 2},
        "toast": "用心做的事，真的会被人看到。",
        "cooldown": 600
    },
    {
        "id": "evt_store_020",
        "name": "困到算错钱",
        "description": "你已经困得不行，给一位顾客找错了零钱。对方数了一下，笑着还给你多找的部分。你连连道歉，她说：'没事，上夜班辛苦了吧。'",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 2, "gold": -2},
        "toast": "困的时候容易出错，还好遇到了好人。",
        "cooldown": 600
    },
    {
        "id": "evt_store_021",
        "name": "台风天坚守岗位",
        "description": "外面刮台风，街上几乎没人。你和店长两个人守着店，听着风声呼啸。店长说今天能来上班的都给双倍。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": 15, "mood": 2, "fatigue": 5},
        "toast": "风雨无阻的打工人。",
        "cooldown": 600
    },
    {
        "id": "evt_store_022",
        "name": "被小朋友崇拜",
        "description": "一个小朋友在店里看到你利落地扫码装袋，眼睛发亮地说：'你好厉害！'你忍不住笑了，这是你今天听到的最真诚的夸奖。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 4, "popularity": 1},
        "toast": "在小朋友眼里，收银员也是超人。",
        "cooldown": 600
    },
    {
        "id": "evt_store_023",
        "name": "店里的背景音乐洗脑",
        "description": "今天便利店的背景音乐一直在循环一首歌，你下班后走在路上脑子里还在放。更可怕的是你开始跟着哼了。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 2, "vocal": 1},
        "toast": "被便利店BGM洗脑的又一天。",
        "cooldown": 600
    },
    {
        "id": "evt_store_024",
        "name": "不小心打碎一瓶饮料",
        "description": "你整理货架时手滑打碎了一瓶玻璃装的果汁。清理了十分钟才弄干净，手上还沾了黏糊糊的橙汁。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": -5, "hygiene": -2, "mood": -2},
        "toast": "碎碎平安……破财消灾……",
        "cooldown": 600
    },
    {
        "id": "evt_store_025",
        "name": "同事分享自制便当",
        "description": "一个同事带了自己做的便当，多出来一份分给了你。虽然卖相一般，但味道意外地好。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"satiety": 6, "mood": 3},
        "toast": "同事的手艺，比便利店的便当好吃十倍。",
        "cooldown": 600
    },
    {
        "id": "evt_store_026",
        "name": "捡到一枚幸运硬币",
        "description": "你扫地时在货架底下发现了一枚闪亮的一元硬币。你把它洗干净放在收银机旁边，觉得这是今天好运的预兆。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": 1, "mood": 1},
        "toast": "一元钱的幸运，不嫌少。",
        "cooldown": 600
    },
    {
        "id": "evt_store_027",
        "name": "顾客帮你捡东西",
        "description": "你搬货时不小心掉了一地零食，一位正在逛店的顾客二话不说蹲下来帮你一起捡。你连声道谢，她笑着说'举手之劳'。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 3, "popularity": 1},
        "toast": "陌生人的举手之劳，能让一天都变好。",
        "cooldown": 600
    },
    {
        "id": "evt_store_028",
        "name": "熟记了常客的喜好",
        "description": "有个常客每天下午三点来买一瓶无糖乌龙茶。你今天远远看到他走过来，提前把茶放在收银台上。他愣了一下，然后笑了。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"popularity": 2, "mood": 2, "fans": 1},
        "toast": "被记住的感觉，大概就是这样吧。",
        "cooldown": 600
    },
    {
        "id": "evt_store_029",
        "name": "便当的试吃福利",
        "description": "今天供货商来推销一款还没上市的新口味饭团，请店员免费试吃。你分到了最大的一块。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"satiety": 4, "mood": 3},
        "toast": "新品试吃员——兼职的隐藏福利。",
        "cooldown": 600
    },
    {
        "id": "evt_store_030",
        "name": "发工资日的奢侈",
        "description": "今天发工资了。你下班后去便利店旁边的甜品店给自己买了一块小蛋糕——平时不舍得买的那款。你在店里慢慢吃完，觉得这是对自己这个月辛苦的奖励。",
        "type": "instant",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"gold": -15, "mood": 5, "satiety": 4},
        "toast": "犒劳自己，是继续努力的动力。",
        "cooldown": 600
    },

    # --------------------------------- Choice ---------------------------------
    {
        "id": "evt_store_031",
        "name": "同事请求代班",
        "description": "一个同事发消息说今晚有急事，想让你帮他代班。但你本来计划今晚去上舞蹈课的。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "答应代班",
                "effects": {"gold": 15, "mood": -1, "dance": 0, "popularity": 2},
                "result": "人情攒下了，舞步落后了。但同事说下次一定还你。"
            },
            {
                "text": "拒绝，坚持自己的计划",
                "effects": {"dance": 3, "mood": 2, "popularity": -1},
                "result": "你守住了自己的时间。学会拒绝是成长的一部分。"
            }
        ]
    },
    {
        "id": "evt_store_032",
        "name": "可疑的顾客",
        "description": "一个穿着连帽衫的年轻人走进来，在货架间徘徊了很久，不停往你的方向瞟。你的直觉告诉你可能有问题，但你又不确定。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "主动过去问他需要什么帮助",
                "effects": {"mood": 2, "acting": 1},
                "result": "主动出击化解了可能的麻烦。"
            },
            {
                "text": "提高警惕但保持距离",
                "effects": {"mood": -1, "fatigue": 1},
                "result": "无事发生。但那种紧张感在你心里多待了一会儿。"
            }
        ]
    },
    {
        "id": "evt_store_033",
        "name": "要不要吃夜宵",
        "description": "深夜下班后，你路过一家还开着的拉面店。肚子咕咕叫，但明天一早还要去上声乐课。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "进去吃一碗热拉面",
                "effects": {"satiety": 8, "mood": 4, "vocal": -1, "gold": -10},
                "result": "美味的代价是嗓子抗议。但你不会后悔的。"
            },
            {
                "text": "忍一忍回家睡觉",
                "effects": {"stamina": 3, "vocal": 1, "mood": -1},
                "result": "自律的感觉比拉面的味道更持久——虽然拉面可能更好吃。"
            }
        ]
    },
    {
        "id": "evt_store_034",
        "name": "店长推荐你做正式员工",
        "description": "店长找你谈话，说觉得你做事认真，问你想不想转正。这意味着更多钱和稳定，但也意味着更少的自由时间。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "接受转正",
                "effects": {"gold": 20, "mood": 1, "fatigue": 3},
                "result": "稳定的生活是好的，但你在日程本上重新规划了练习时间。"
            },
            {
                "text": "婉拒，告诉店长你还有其他梦想",
                "effects": {"mood": 3, "popularity": 2},
                "result": "店长成了你的理解者。兼职还在，梦想也在。"
            }
        ]
    },
    {
        "id": "evt_store_035",
        "name": "顾客情绪崩溃",
        "description": "一位女顾客在店里突然蹲下来哭了。你不知道发生了什么，周围的顾客都在看着你。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "递上一包纸巾和一瓶温水",
                "effects": {"mood": 2, "charm": 2, "popularity": 2},
                "result": "你没有问为什么，但她感受到了被尊重。"
            },
            {
                "text": "问一句'你还好吗'",
                "effects": {"mood": 3, "fans": 2, "popularity": 1},
                "result": "她走的时候回头看了一下你。有些温暖来自于被看见。"
            }
        ]
    },
    {
        "id": "evt_store_036",
        "name": "要不要举报同事偷懒",
        "description": "你发现有一个同事每次夜班都在仓库偷偷打游戏，把大部分工作都推给你。店长似乎不知道这件事。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "私下和他谈一谈",
                "effects": {"mood": 2, "popularity": 1},
                "result": "正面沟通比背后举报更需要勇气。你做到了。"
            },
            {
                "text": "忍一忍，不想惹事",
                "effects": {"mood": -2, "fatigue": 3},
                "result": "忍耐是一种选择，但忍耐也有代价。"
            }
        ]
    },
    {
        "id": "evt_store_037",
        "name": "捡到一个没上锁的手机",
        "description": "你在货架间发现一部手机，屏幕还亮着，没有锁屏密码。通讯录和支付软件都能打开。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "立刻交给店长保管",
                "effects": {"mood": 3, "popularity": 3},
                "result": "失主说你救了他半条命。虽然有点夸张，但你挺开心的。"
            },
            {
                "text": "在店里等失主自己来找",
                "effects": {"mood": 1},
                "result": "你没有经手，但也守护了它。"
            }
        ]
    },
    {
        "id": "evt_store_038",
        "name": "要不要参加便利店总部的技能大赛",
        "description": "总部要举办一个收银速度大赛，店长推荐了你。但你最近正在准备一个声乐班的表演。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "参加大赛",
                "effects": {"gold": 10, "mood": 3, "popularity": 4},
                "result": "收银技能大赛第三名——可以写进简历吗？"
            },
            {
                "text": "婉拒，专心准备声乐表演",
                "effects": {"vocal": 3, "mood": 2},
                "result": "舞台上的发挥，证明你的选择没有错。"
            }
        ]
    },
    {
        "id": "evt_store_039",
        "name": "同事找你借钱",
        "description": "一个不算太熟的工友问你借五百块，说家里有急事，下周发工资就还。他看上去确实很着急。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "借给他",
                "effects": {"gold": 0, "popularity": 3, "mood": 2},
                "result": "信任被兑现了。这种感觉很好。"
            },
            {
                "text": "委婉说最近自己也很紧",
                "effects": {"mood": -1},
                "result": "拒绝别人的感觉不太好，但你确实需要为自己的生活打算。"
            }
        ]
    },
    {
        "id": "evt_store_040",
        "name": "要不要指出店长的错误",
        "description": "店长在排班上把你的工时算少了一个小时。你很确定，但店长最近压力很大，脾气不太好。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "委婉地提醒",
                "effects": {"gold": 5, "mood": 2},
                "result": "有理有据有礼貌——这是争取自己权益的正确方式。"
            },
            {
                "text": "算了，一个小时而已",
                "effects": {"mood": -1, "gold": 0},
                "result": "吃亏是福？有时候只是安慰自己的话。"
            }
        ]
    },
    {
        "id": "evt_store_041",
        "name": "夜班的独自坚守",
        "description": "今晚另一个值夜班的同事请病假，店长问你能不能一个人扛整晚。这意味着一整晚不能合眼，但店长说会给你额外的夜班津贴。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "接下这个挑战",
                "effects": {"gold": 25, "fatigue": 15, "mood": 3, "stamina": -8},
                "result": "一个人守了一整夜。累到骨头里，但津贴和成就感是真的。"
            },
            {
                "text": "婉拒，说自己一个人撑不下来",
                "effects": {"mood": -1, "fatigue": 0},
                "result": "诚实面对自己的极限也是一种成熟。"
            }
        ]
    },
    {
        "id": "evt_store_042",
        "name": "店里来了一个流浪汉",
        "description": "一个流浪汉走进来，身上有味道，在暖食区站了很久。几个顾客皱起了眉头，有人看向你。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "让他待一会儿，给他一份热食",
                "effects": {"mood": 5, "popularity": 3, "gold": -5},
                "result": "店长后来知道了，说'下次别自己掏钱，店里请'。"
            },
            {
                "text": "礼貌地请他不要影响其他顾客",
                "effects": {"mood": -2, "popularity": 1},
                "result": "你执行了职责，但心里好像多了点什么。"
            }
        ]
    },
    {
        "id": "evt_store_043",
        "name": "要不要买便利店员工折扣的瑕疵品",
        "description": "便利店有一批包装破损但不影响使用的日用品，员工可以以两折购买。你正好需要一些东西，但买瑕疵品总觉得有点委屈自己。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "买，实用主义至上",
                "effects": {"gold": 5, "mood": 3},
                "result": "实用主义的胜利。省下的钱可以买别的。"
            },
            {
                "text": "不买，不想将就",
                "effects": {"mood": 1},
                "result": "为品质付费，也是为心情付费。"
            }
        ]
    },
    {
        "id": "evt_store_044",
        "name": "发现货架上有一件商品被恶作剧换了位置",
        "description": "有人在零食区把一包薯片拆开，把里面的薯片换成了膨化玉米条，然后用胶带封了回去。你发现了这个'作案现场'。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "拍照发工作群吐槽",
                "effects": {"mood": 3, "popularity": 2},
                "result": "工作群因为一包被调包的薯片活跃了起来。"
            },
            {
                "text": "默默处理掉",
                "effects": {"mood": -1},
                "result": "你处理了无聊的恶作剧，保持了专业。"
            }
        ]
    },
    {
        "id": "evt_store_045",
        "name": "要不要在便利店里练声",
        "description": "凌晨没人，店里很安静。你突然想小声练一会儿声乐课上学的发声练习。店长不在，只有一个同事在仓库理货。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "小声练一会儿",
                "effects": {"vocal": 2, "mood": 3},
                "result": "便利店变成了你的第一个练歌房。"
            },
            {
                "text": "忍住，回家再练",
                "effects": {"mood": 1, "acting": 1},
                "result": "自律的你在心里默默期待一个更好的练习环境。"
            }
        ]
    },
    {
        "id": "evt_store_046",
        "name": "被顾客问'你是不是在学唱歌'",
        "description": "一个顾客在结账时忽然说：'你的声音条件好像不错，你是不是在学唱歌？'你愣住了——他是怎么看出来的？",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "老实承认并聊下去",
                "effects": {"vocal": 2, "mood": 3, "fans": 1},
                "result": "在便利店遇到了半个同行，收获了一个好方法。"
            },
            {
                "text": "谦虚地说只是爱好",
                "effects": {"mood": 2, "charm": 1},
                "result": "被看出来有天分，虽然你嘴上说只是爱好。"
            }
        ]
    },
    {
        "id": "evt_store_047",
        "name": "加班还是去朋友的聚会",
        "description": "几个很久没见的朋友约今晚聚会。但你今天已经答应了同事帮忙顶一个小时的班，再加班的话聚会就来不及了。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "准时下班去聚会",
                "effects": {"mood": 5, "popularity": 2},
                "result": "友情是需要维护的。今晚的笑声是最好的充电。"
            },
            {
                "text": "留下来把工作做好",
                "effects": {"gold": 5, "mood": 1, "popularity": 1},
                "result": "工作第一，但朋友还在等你。这样也不错。"
            }
        ]
    },
    {
        "id": "evt_store_048",
        "name": "要不要在店里办小型分享会",
        "description": "一个独立音乐人经常来店里买咖啡，今天他试探性地问你能不能周末晚上借用便利店的一角办一个迷你弹唱会，就半小时，他自己搬设备。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "帮你向店长申请",
                "effects": {"popularity": 5, "mood": 4, "fans": 3},
                "result": "一家便利店，也可以有live演出。"
            },
            {
                "text": "礼貌拒绝",
                "effects": {"mood": -1},
                "result": "理性拒绝是对的，但你忍不住想象了一下那个画面。"
            }
        ]
    },
    {
        "id": "evt_store_049",
        "name": "遇到了来买东西的舞蹈老师",
        "description": "你的街舞课老师推门进来买东西，正好看到你在收银台后面。你们四目相对，都愣了一下。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "自然地打招呼",
                "effects": {"mood": 4, "dance": 1, "popularity": 1},
                "result": "老师和学生的便利店偶遇——下次上课他还是没手下留情。"
            },
            {
                "text": "有点不好意思，假装没认出来",
                "effects": {"mood": -1, "acting": 1},
                "result": "假装不认识失败。下次还是大方打招呼吧。"
            }
        ]
    },
    {
        "id": "evt_store_050",
        "name": "要不要为了省钱自己带饭",
        "description": "你已经连续一个月在便利店解决三餐了，不算贵但加起来也是一笔开销。同事建议你自己带饭，说能省不少。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "开始自己带饭",
                "effects": {"gold": 10, "satiety": 3, "hygiene": 1},
                "result": "省钱技能+1，厨艺技能+0.5。"
            },
            {
                "text": "继续在便利店解决",
                "effects": {"mood": 1, "gold": -3},
                "result": "时间就是金钱——或者说，时间比金钱更值钱。"
            }
        ]
    },
    {
        "id": "evt_store_051",
        "name": "顾客找你换零钱但金额不对",
        "description": "一位顾客急急忙忙拿着一张五十块说想换零钱坐公交，但你打开收银机发现零钱不够换五十块。你只能换一部分。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "换了多少是多少",
                "effects": {"mood": 2, "popularity": 1},
                "result": "帮到一点是一点。"
            },
            {
                "text": "建议他去隔壁店试试",
                "effects": {"mood": 0},
                "result": "你给了最合理的建议，虽然没能直接帮上忙。"
            }
        ]
    },
    {
        "id": "evt_store_052",
        "name": "要不要学店长的管理方式",
        "description": "店长最近在教你一些库存管理和排班的技巧，说'以后你不管做哪一行，这些都有用'。但这意味着你要花额外的时间学习。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "认真学习管理知识",
                "effects": {"acting": 2, "mood": 2, "gold": 0},
                "result": "多学一点总是好的。技多不压身。"
            },
            {
                "text": "先专注手头的工作和练习",
                "effects": {"mood": 1, "dance": 1},
                "result": "你对自己的时间分配很清醒。"
            }
        ]
    },
    {
        "id": "evt_store_053",
        "name": "收到了顾客的投诉",
        "description": "一位顾客投诉你态度不好。你回想了一下，觉得自己确实可能因为太累了声音有点冷淡。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "主动向顾客道歉并改进",
                "effects": {"mood": 2, "popularity": 3},
                "result": "道歉没有让你变矮，反而让你变高了。"
            },
            {
                "text": "心里不服但接受处理",
                "effects": {"mood": -2},
                "result": "有时候委屈也只能咽下去。"
            }
        ]
    },
    {
        "id": "evt_store_054",
        "name": "要不要参与便利店的轮岗",
        "description": "店长说想让你去其他分店轮岗一个月，算是培训的一部分。那家店离你的舞蹈教室更近。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "接受轮岗",
                "effects": {"dance": 2, "mood": 3, "popularity": 2},
                "result": "换个环境，换个节奏，有时候是意外的收获。"
            },
            {
                "text": "留在熟悉的店里",
                "effects": {"mood": 1, "stamina": 1},
                "result": "安稳也是一种选择。不是每个人都必须不停地变。"
            }
        ]
    },
    {
        "id": "evt_store_055",
        "name": "发现了同事藏起来的零食",
        "description": "你在整理仓库时发现了一个纸箱，里面全是同事私藏的限量版零食——是他用自己的员工折扣买的，打算囤着慢慢吃。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "假装没看到",
                "effects": {"popularity": 2, "mood": 1},
                "result": "保守秘密的人，会被当成自己人。"
            },
            {
                "text": "开玩笑说'被我发现了'",
                "effects": {"satiety": 3, "mood": 3, "popularity": 2},
                "result": "秘密变成了分享的借口。"
            }
        ]
    },
    {
        "id": "evt_store_056",
        "name": "店里的背景音乐能不能换",
        "description": "便利店的背景音乐是一个固定的播放列表，你已经听了好几个月，每一首歌的播放顺序都烂熟于心。今天你终于忍不住问店长能不能换一个列表。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "向店长提议换歌单",
                "effects": {"mood": 3, "popularity": 1},
                "result": "换歌单成功！同事们都说新列表好听。"
            },
            {
                "text": "忍了，反正也习惯了",
                "effects": {"mood": -1},
                "result": "熟悉感有时候也是一种舒适区。"
            }
        ]
    },
    {
        "id": "evt_store_057",
        "name": "顾客在店里过夜",
        "description": "寒潮来袭的夜晚，一个老人走进店里，在休息区坐了很久，似乎想在这里过夜。外面气温已经降到零下。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "默许他待着，给他倒一杯热水",
                "effects": {"mood": 4, "popularity": 2},
                "result": "一杯热水和一个温暖的角落，也许救了一条命。"
            },
            {
                "text": "按规定请他在营业时间结束前离开",
                "effects": {"mood": -3, "popularity": 1},
                "result": "你做了对的事，但那一晚你一直想起他的背影。"
            }
        ]
    },
    {
        "id": "evt_store_058",
        "name": "要不要把便利店当成练习观察场所",
        "description": "你忽然意识到便利店是一个绝佳的'人物观察室'——每天有各种各样的人进进出出，每种表情、每个动作，都是表演课的素材。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "开始有意识地观察并记录",
                "effects": {"acting": 3, "mood": 2},
                "result": "便利店变成了你的表演素材库。每个顾客都是你的老师。"
            },
            {
                "text": "觉得这样有点奇怪",
                "effects": {"mood": 0},
                "result": "你选择尊重他人的边界，也是一种职业素养。"
            }
        ]
    },
    {
        "id": "evt_store_059",
        "name": "晚班遇到了停电",
        "description": "整个街区突然停电，便利店里一片漆黑。应急灯亮起后，你成了店里唯一能安抚顾客的人。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "用这段时间和顾客聊天",
                "effects": {"popularity": 3, "mood": 4},
                "result": "停电让陌生人变成了临时的朋友。"
            },
            {
                "text": "有条不紊地按应急预案处理",
                "effects": {"mood": 2, "gold": 5, "popularity": 1},
                "result": "你的冷静和专业被看到了。"
            }
        ]
    },
    {
        "id": "evt_store_060",
        "name": "要不要主动提出改进建议",
        "description": "你发现便利店的货架布局有些不合理——畅销品放在太靠里的位置，顾客经常找不到。你有一个改进的想法。",
        "type": "choice",
        "trigger_condition": None,
        "weight": 10,
        "effects": {},
        "toast": "",
        "cooldown": 900,
        "choices": [
            {
                "text": "向店长提出你的建议",
                "effects": {"mood": 4, "gold": 5, "charm": 2},
                "result": "你的建议被采纳了。原来自己的观察是有价值的。"
            },
            {
                "text": "算了，多一事不如少一事",
                "effects": {"mood": -1},
                "result": "你忍住了没说，但那个想法一直卡在你喉咙里。"
            }
        ]
    },

    # --------------------------------- Narrative ---------------------------------
    {
        "id": "evt_store_061",
        "name": "收银台上的蚂蚁",
        "description": "凌晨收银台上爬过一只蚂蚁。你看着它从键盘的1爬到0，然后消失了。你忽然想，这只蚂蚁知不知道自己在人类的收银台上走了一遭？就像你不知道自己的人生正在哪个更大的舞台上走过。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_062",
        "name": "窗外的猫",
        "description": "便利店门口经常蹲着一只橘猫。你不忙的时候会隔着玻璃看它，它偶尔也会看你一眼。你们之间没有任何交流，但你觉得自己和这只猫有了某种默契。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_063",
        "name": "荧光灯的声音",
        "description": "夜班的时候，你第一次注意到便利店头顶的荧光灯会发出非常细微的嗡鸣声。这个声音一直都在，但只有足够安静的时候才能听见。你想，很多事大概都是这样。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_064",
        "name": "保温柜里的包子",
        "description": "保温柜里的包子在暖黄色的灯光下冒着热气。你盯着它们久了，觉得它们像一排胖嘟嘟的观众，正在无声地看你工作。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_065",
        "name": "工资到账的短信",
        "description": "手机亮了，工资到账的短信跳出来。数字不多，但每一块都是你自己挣的。你看着那个数字，第一次觉得'独立'这个词有了具体的形状。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_066",
        "name": "玻璃门上的倒影",
        "description": "深夜，便利店的玻璃门变成了一面镜子。你看着倒影里穿着制服的自己，忽然开始想象——如果这个倒影换上演出服站在舞台上，会是什么样子？",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_067",
        "name": "被翻乱的杂志架",
        "description": "你整理杂志架的时候发现有一本杂志被翻到了某一页，那一页上是一个新出道偶像的采访。你看了看那页的内容——'从零开始，每天练习十二个小时。'你把那本杂志放回原位，但记住了那句话。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_068",
        "name": "自动门的节奏",
        "description": "自动门开合的声音有它自己的节奏。你发现周六晚上的'叮咚'比周一早上密集很多。这扇门像一首歌的节拍器，记录着这条街的脉搏。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_069",
        "name": "咖啡机的蒸汽",
        "description": "凌晨做咖啡的时候，蒸汽喷出来的声音很好听。你下意识地用这个音高哼了一下。一个你从来没在声乐课上发出过的音，在这个安静的凌晨，从便利店的咖啡机前飘了出来。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"vocal": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_070",
        "name": "陌生的外卖骑手",
        "description": "一个外卖骑手进来取订单，他的手机壳上贴着一个乐队的logo——是你也很喜欢的那支乐队。你们对视了一秒，他赶时间去送餐，你没来得及开口。但你知道这条街上有一个和你听一样音乐的人。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_071",
        "name": "雨夜的橱窗",
        "description": "外面下着大雨，你透过便利店的玻璃窗看出去，街道被雨水冲刷得很干净。有一辆车经过，车灯在湿漉漉的路面上拉出长长的光。你想，这个画面如果写成歌词，应该配一个很温柔的前奏。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_072",
        "name": "便当的保质期标签",
        "description": "你在更换便当的保质期标签时，看到标签上印着'请在明日之前食用'。你想，人是没有保质期的。你可以慢慢来。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_073",
        "name": "深夜便利店和凌晨的界限",
        "description": "凌晨四点五十九分和五点好像没有什么区别，但天空的颜色确实不一样了。你在收银台后面见证了这个变化。你是这个城市从深夜过渡到黎明的目击者。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_074",
        "name": "伞桶里的遗忘",
        "description": "门口的伞桶里有一把被遗忘的透明雨伞。它在那里放了一周，没有人回来取。你每次整理伞桶的时候都会看到它。有一天它终于不见了——你不知道是失主回来了，还是别人拿走了。你在心里祝这把伞好运。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_075",
        "name": "下班后的便利店",
        "description": "你作为顾客在下班后走进另一家便利店买水。收银员对你说'欢迎光临'，你愣了一下，然后笑了。这个声音你很熟悉，你每天要说几百遍。现在你站在顾客的位置上，忽然明白了那句话的另一面——它不只是职业用语，也是一个普通人对另一个普通人的问候。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_076",
        "name": "制服口袋里的东西",
        "description": "下班前你翻了一下制服口袋，里面有：一张揉皱的收银小票、一颗薄荷糖、一支笔帽裂了的圆珠笔、和一个不知道什么时候放进去的发圈。每一样东西都代表今天的一个瞬间。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_077",
        "name": "货架间的过道",
        "description": "深夜整理货架时，你站在两排货架之间的过道上，忽然觉得这条过道很像一条小小的走廊。你每天在这条走廊上走几百个来回，从饮料走到零食，从零食走到日用品。这条路不长，但你已经走了几千遍。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_078",
        "name": "冷柜的灯光",
        "description": "冷柜里的灯光是冷白色的，照在每一瓶饮料上。你在补货的时候盯着这排灯光看了很久，觉得它们像一排小小的舞台灯，而矿泉水瓶是沉默的观众。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_079",
        "name": "半夜的加油站",
        "description": "便利店隔壁的加油站半夜也很安静。透过便利店的玻璃，你能看到加油站的红色顶棚在夜风里微微晃动。你忽然觉得便利店的灯光和加油站的灯光，是这个夜晚相依为命的两座灯塔。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_080",
        "name": "一个没买任何东西的人",
        "description": "有一个人进店后什么也没买，只是在店里走了一圈，然后站在杂志架前翻了翻封面，最后深吸一口气走了出去。你不知道他经历了什么，但你觉得他进来不是为了买东西，而是为了找一个有灯光和人声的地方待一会儿。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_081",
        "name": "硬币的声音",
        "description": "你交班时把收银机里的硬币倒进袋子，硬币碰撞的声音在安静的店里格外清脆。这个声音每次听到都让你觉得一天结束了，很踏实。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_082",
        "name": "夜班和早班的交接",
        "description": "夜班结束的时候早班的同事来了。你们在收银台后面擦肩而过，她说了句'辛苦了'，你回了句'交给你了'。这几个字是你们之间最常说的话，但每次听到都让人觉得温暖。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_083",
        "name": "便利店的气味",
        "description": "便利店有一种独特的气味——消毒水、印刷油墨、热食和冷气混合在一起的味道。你在别的地方闻到类似的味道时，会下意识地想回头说'欢迎光临'。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_084",
        "name": "被水汽模糊的冷柜门",
        "description": "冷柜的门被外面的热气蒙上了一层水雾。你用手擦了一下，透过那块干净的玻璃看到了里面整整齐齐的饮料。这个动作你今天重复了十几遍，但每次擦完都觉得很解压。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_085",
        "name": "深夜的货车",
        "description": "凌晨有一辆货车停在店门口补货。司机从车上搬下来一箱一箱的便当和饮料，动作利落得像一种舞蹈。你给他递了一瓶水，他接过去一口喝完，说了句'谢了兄弟/姐妹'。然后他上车开走了，便利店的货架上又多了一天的食物。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_086",
        "name": "贴标签的手",
        "description": "你今天贴了几百张价格标签。下班后你发现自己的大拇指上还粘着一小片标签纸的背胶。你把它撕下来，觉得这个小碎片是你今天工作的最后一块拼图。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_087",
        "name": "便利店的海报",
        "description": "店门口换了一张新海报，是当季的限量草莓甜品。你贴海报的时候在想，也许有一天，你也会出现在某张海报上，被另一个人贴在便利店的门口。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_088",
        "name": "同一个时间同一个位置",
        "description": "你发现自己每天凌晨三点十五分左右，都会在同一个位置擦同一块地砖。这件事没有任何意义，但你每天都在做。也许习惯就是这样——一些没有意义但让你觉得安心的重复。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_089",
        "name": "窗外的第一场雪",
        "description": "今年冬天的第一场雪在夜班时落下来了。你隔着便利店的玻璃窗看到雪花在路灯下飞舞，整条街都安静了下来。你站在窗前看了很久，直到自动门'叮咚'一声把你拉回来。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    },
    {
        "id": "evt_store_090",
        "name": "把制服挂回柜子",
        "description": "下班后你把制服叠好放进储物柜。柜门关上之前，你看了它一眼——这件制服陪了你又一个普通的日子。你知道这件制服不会是你永远的制服，但你会记得它。",
        "type": "narrative",
        "trigger_condition": None,
        "weight": 10,
        "effects": {"mood": 1},
        "toast": "",
        "cooldown": 300
    }
]


# ==================== 选择窗口 ====================
class ChoiceWindow:
    """用于显示二选一事件的小窗口"""
    def __init__(self, parent, event, on_choose, pet_x, pet_y, pet_w, pet_h):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.configure(bg="#2E2E2E")
        self.win.attributes("-alpha", 0.95)
        
        # 窗口尺寸
        w, h = 360, 220
        
        # 固定在宠物头顶正上方
        x = pet_x + (pet_w - w) // 2
        y = pet_y - h - 10  # 宠物上方10像素
        # 防止超出屏幕上边界
        if y < 0:
            y = pet_y + pet_h + 10
        self.win.geometry(f"{w}x{h}+{x}+{y}")
        
        # 事件标题
        name_label = tk.Label(self.win, text=event.get("name", ""), 
                              font=("微软雅黑", 11, "bold"), fg="#FFD700", bg="#2E2E2E")
        name_label.pack(pady=(15, 5))
        
        # 事件描述（自动换行，最多显示4行）
        desc_label = tk.Label(self.win, text=event["description"], 
                              font=("微软雅黑", 10), fg="white", bg="#2E2E2E",
                              wraplength=320, justify="left")
        desc_label.pack(pady=(0, 10), padx=20)
        
        # 按钮框架
        btn_frame = tk.Frame(self.win, bg="#2E2E2E")
        btn_frame.pack(pady=5)
        
        def make_choice(choice_idx):
            self.win.destroy()
            choice = event["choices"][choice_idx]
            on_choose(choice)
        
        for i, choice in enumerate(event["choices"]):
            # 选项文字如果超过18个字就截断加省略号
            btn_text = choice["text"]
            if len(btn_text) > 18:
                btn_text = btn_text[:17] + "…"
            
            btn = tk.Button(btn_frame, text=btn_text, 
                            font=("微软雅黑", 9), fg="white",
                            bg="#555555" if i==0 else "#444444",
                            activebackground="#777777",
                            width=18, height=2,
                            wraplength=140,       # 按钮内文字超过140像素自动换行
                            command=lambda idx=i: make_choice(idx))
            btn.pack(side=tk.LEFT, padx=12)
        
        # 底部提示
        tip_label = tk.Label(self.win, text="请选择一个选项（不会自动关闭）", 
                             font=("微软雅黑", 8), fg="#999999", bg="#2E2E2E")
        tip_label.pack(pady=(10, 5))


# ==================== 事件调度器 ====================
class EventScheduler:
    def __init__(self, pet_state, toast_callback, info_callback):
        """
        pet_state: PetState 实例
        toast_callback: 用于显示短暂提示的函数 (msg, duration)
        info_callback: 用于显示弹窗消息的函数 (msg)
        """
        self.state = pet_state
        self.toast = toast_callback
        self.info = info_callback
        
        # 冷却记录：{event_id: last_trigger_timestamp}
        self.cooldowns = {}
        # 从存档加载冷却记录
        if hasattr(pet_state, 'event_cooldowns'):
            self.cooldowns = pet_state.event_cooldowns
        
        # 下次事件检查时间（初始设为5分钟后）
        self.next_check_time = time.time() + 10
        
        # 用于存储当前打开的选择窗口，避免同时打开多个
        self.current_choice_win = None
    
    def update(self, parent_window):
        """在 companion_loop 中每秒调用一次"""
        # 专注模式或体力耗尽休息时不触发事件
        if self.state.focus_mode or self.state.resting:
            return
        
        now = time.time()
        if now < self.next_check_time:
            return
        
        # 重置下次检查时间（5~30分钟随机间隔）
        self.next_check_time = now + 30   # 每次等 30 秒就尝试触发
        
        # 概率检查（50%）
        if random.random() > 0.5:
            return
        
        # 筛选可用事件：冷却结束、无状态条件限制
        available = []
        for event in EVENT_POOL:
            if not self._check_cooldown(event, now):
                continue
            if event["trigger_condition"]:
                # 如果以后加了复杂的条件判断，可以在这里扩展
                if not self._check_conditions(event["trigger_condition"]):
                    continue
            available.append(event)
        
        if not available:
            return
        
        # 按权重随机选择
        total_weight = sum(ev.get("weight", 10) for ev in available)
        rand = random.uniform(0, total_weight)
        cumulative = 0
        chosen = None
        for ev in available:
            cumulative += ev.get("weight", 10)
            if rand <= cumulative:
                chosen = ev
                break
        
        if chosen:
            self.trigger_event(chosen, parent_window)
    
    def _check_cooldown(self, event, now):
        """检查事件是否在冷却中"""
        eid = event["id"]
        if eid in self.cooldowns:
            last = self.cooldowns[eid]
            cooldown_sec = event.get("cooldown", 0)
            if now - last < cooldown_sec:
                return False
        return True
    
    def _check_conditions(self, conditions):
        """预留：检查复杂的触发条件"""
        return True
    
    def trigger_event(self, event, parent_window):
        """执行事件效果并显示 UI"""
        etype = event["type"]
        
        # 记录冷却
        self.cooldowns[event["id"]] = time.time()
        self._save_cooldowns()
        
        if etype == "instant":
            effects = event["effects"]
            self._apply_effects(effects)
            # 构造效果文字
            effect_text = self._format_effects(effects)
            toast_msg = event.get("toast", event["description"])
            if effect_text:
                toast_msg = toast_msg + "\n" + effect_text
            self.toast(toast_msg, 4000)  # 延长到4秒，方便看效果
        
        elif etype == "narrative":
            if event["effects"]:
                self._apply_effects(event["effects"])
            self.info(event["description"])
        
        elif etype == "choice":
            if self.current_choice_win and self.current_choice_win.win.winfo_exists():
                return
            # 获取宠物窗口位置和尺寸
            pet_x = parent_window.winfo_rootx()
            pet_y = parent_window.winfo_rooty()
            pet_w = parent_window.winfo_width()
            pet_h = parent_window.winfo_height()
            self.current_choice_win = ChoiceWindow(
                parent_window,
                event,
                lambda choice: self._on_choice_made(event, choice),
                pet_x, pet_y, pet_w, pet_h
            )

    def _format_effects(self, effects):
        """将效果字典格式化为可读文字，如：饱食+5  心情+3  金币-10"""
        if not effects:
            return ""
        name_map = {
            "satiety": "饱食", "stamina": "体力", "hygiene": "清洁", "mood": "心情",
            "gold": "金币", "vocal": "唱功", "dance": "舞蹈", "acting": "演技",
            "variety": "综艺", "charm": "魅力", "popularity": "人气", "fans": "粉丝",
            "fatigue": "疲劳", "sick": "生病"
        }
        parts = []
        for attr, val in effects.items():
            if attr == "sick":
                parts.append("生病了！" if val else "")
                continue
            display = name_map.get(attr, attr)
            if val > 0:
                parts.append(f"{display}+{val}")
            elif val < 0:
                parts.append(f"{display}{val}")  # 负号自动带
        return "  ".join(parts)
    
    def _on_choice_made(self, event, choice):
        if choice is None:
            return
        effects = choice["effects"]
        self._apply_effects(effects)
        # 显示选项结果 + 具体效果
        result_text = choice.get("result", "")
        effect_text = self._format_effects(effects)
        if result_text and effect_text:
            self.info(result_text + "\n" + effect_text)
        elif result_text:
            self.info(result_text)
        elif effect_text:
            self.info(effect_text)
    
    def _apply_effects(self, effects):
        """将效果字典应用到 PetState"""
        s = self.state
        for attr, value in effects.items():
            # 特殊处理 sick 为布尔值
            if attr == "sick":
                if value:
                    s.sick = True
                # 注意：如果需要治愈事件，可设置 "sick": False
                continue
            
            current = getattr(s, attr, 0)
            # 对大部分属性进行加法操作，并限制范围（如果有范围要求）
            if attr in ("satiety", "stamina", "hygiene", "mood"):
                setattr(s, attr, max(0, min(100, current + value)))
            elif attr == "fatigue":
                setattr(s, attr, max(0, min(100, current + value)))
            elif attr in ("gold", "fans", "popularity"):
                setattr(s, attr, max(0, current + value))
            else:
                # 无上限属性：vocal, dance, acting, charm 等
                setattr(s, attr, max(0, current + value))
        s.save()
    
    def _save_cooldowns(self):
        """将冷却记录写回 pet_state，以便存档"""
        self.state.event_cooldowns = self.cooldowns
