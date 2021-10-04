from datetime import date as m_date
from json import load, dump
from os.path import exists, join
from random import randint
from time import localtime, struct_time
from typing import Union, List, Dict

from borax.calendars import LunarDate
from mcdreforged.plugin.server_interface import PluginServerInterface


class FakeDayError(Exception):
    def __init__(self, name, is_date, **reason):
        self.name = name
        self.is_date = is_date
        self.reason = reason

    def __str__(self):
        template = "The %s %s has fake %s: %s"
        if self.is_date:
            return template % ("date", self.name, self.reason["reason"], self.reason["content"])
        else:
            return template % ("day", self.name, self.reason["reason"], self.reason["content"])


DAYS_PER_MONTH = [-1, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DEFAULT_WISH_DAYS = [
    {
        "name": "元旦",
        "type": "Solar",
        "date": (1, 1),
        "message": [
            "岁月如歌蝶恋花，新年朝阳艳如画。元旦喜庆福相随，天地共舞春又归。白雪纷飞送福至，红霞满天寄心意。真诚话语不多说，敬祝佳节多快乐。",
            "新年新开端，首选是元旦。立志好人缘，天天露笑脸。健康常相伴，饮食加锻炼。好运在蛇年，快乐过元旦。祝：元旦快乐！"
        ]
    },
    {
        "name": "腊八节",
        "type": "Lunar",
        "date": (12, 8),
        "message": "称一两开心小米，抓一把吉祥花生，拣几颗健康红枣，挑两粒幸福莲子，加半勺甜蜜清水，用成功之火，炖成一锅香甜如意腊八粥。"
                   "尝一口，一切顺手；尝两口，万事不愁。腊八快乐！"
    },
    {
        "name": "除夕",
        "type": "Lunar",
        "date": (12, 30),
        "message": [
            "除夕之夜来守岁，大年三十来贺岁，岁岁平安吉星照，年年福寿又安康。",
            "除夕夜温馨的氛围：烟火、钟声、灯影以及我这小小的祝福；传达着节日的讯息：快乐、和谐、平安。"
        ]
    },
    {
        "name": "母亲节",
        "type": "Week",
        "date": (5, 2, 6),
        "message": [
            "世上只有妈妈好，投入妈妈怀抱，困难也能看作宝，勤奋努力步步高，如意幸福都来到，祝天下母亲节日快乐，身体健康，平安吉祥!",
            "让我们多给母亲一点爱与关怀，那怕是酷暑中的一把扇子;寒冬中的一件毛衣，让母亲时刻感受儿女的关心，母亲节快乐!"
        ]
    },
    {
        "name": "父亲节",
        "type": "Week",
        "date": (6, 3, 6),
        "message": [
            "不需言语体现，就如此刻你静静体味我诚挚的问候，祝父亲节快乐!",
            "白云从不向天空承诺去留，却朝夕相伴;风景从不向眼睛说出永恒，却始终美丽;我没有常同你联系，却永远牵挂，祝父亲节快乐。"
        ]
    },
    {
        "name": "端午节",
        "type": "Lunar",
        "date": (5, 5),
        "message": [
            "春天种子，夏天粽子，春种忙，忙来春风得意，夏粽香，香来“粽”得圆满。又是一年端午，祝你：事业如春风，得意！爱情如夏粽，圆满！节日快乐！",
            "风，带来轻松；水，带来温柔；雾，带来朦胧；海，带来宽容；月，带来温馨；日，带来热情；我，带来真心的祝福，祝端午节快乐。"
        ]
    },
    {
        "name": "教师节",
        "type": "Solar",
        "date": (9, 10),
        "message": [
            "教师节，我托阳光送你美好的祝愿，我托秋风带给你深深的思念，我寄白云捎给你久久的惦念，我挟蓝天传给你真真的问候，辛苦了，敬爱的老师。",
            "您是人类灵魂的工程师，您从事的是太阳底下最光辉的事业，您是社会文明进步的阶梯。无尽的恩情，永远铭记心中。在这个属于教师的日子里，深深祝福您！"
        ]
    },
    {
        "name": "中秋节",
        "type": "Lunar",
        "date": (8, 15),
        "message": [
            "月圆年年相似，你我岁岁相盼。那满天的清辉，遍地水银，便是我们互倾的思念。",
            "天上最美是圆月，人间最美中秋节。秋水长天共一色，花好月圆思切切。中秋来临之际，愿君幸福无忧烦恼歇。"
        ]
    },
    {
        "name": "国庆节",
        "type": "Solar",
        "date": (10, 1),
        "message": [
            "祝愿祖国繁荣昌盛，日子越过越红火！",
            "祝祖国国泰民安，愿朋友幸福永伴！"
            "真诚祝愿发自心，祝愿祖国明天更辉煌！"
        ]
    },
    {
        "name": "国庆节",
        "type": "Lunar",
        "date": (9, 9),
        "message": [
            "九九重阳来相聚，友谊久久不分离;重阳糕点来同享，感情牢得不分离;菊花酒举杯共饮，烦恼忧愁统统消，快乐久久来伴随。祝你重阳佳节幸福久久。",
            "笑迎风，乐随景，重阳随秋清凉，舒怀笑，尽情歌，久久时光幸福多，梦中情，梦外心，真情兄弟贵似金，天久长，地久远，久久祝福重阳欢。"
        ]
    },
    # {
    #     "name": "Thanksgiving Day",
    #     "type": "Week",
    #     "date": (11, 4, 3),
    #     "message": [
    #         "We are so grateful for you and your family! Sending you peace and warmth during this crazy time.",
    #         "We hope you and your family have been able to get together "
    #         "this year and are enjoying a Thanksgiving feast together! "
    #     ]
    # }
    {
        "name": "国庆节",
        "type": "Solar",
        "date": (12, 25),
        "message": "圣诞快乐！平安夜，舞翩阡。雪花飘，飞满天。心与心，永相伴。"
    }
]


def check_legitimacy(days: list):
    for day in days:
        if not bool(day["name"]):
            raise FakeDayError(day["date"], True, reason="name", content="empty name")
        if day["type"] not in ["Lunar", "Solar", "Week"]:
            raise FakeDayError(day["name"], False, reason="type", content=day["type"])
        if day["type"] == "Lunar" or day["type"] == "Solar":
            if len(day["date"]) != 2:
                raise FakeDayError(day["name"], False, reason="date", content="not equal to two numbers")
            else:
                if (0 >= day["date"][0] or day["date"][0] > 12) or (
                        0 >= day["date"][1] or day["date"][1] >= DAYS_PER_MONTH[day["date"][0]]):
                    raise FakeDayError(day["name"], False, reason="date", content="invalid date")
        else:
            if len(day["date"]) != 3:
                raise FakeDayError(day["name"], False, reason="date", content="not equal to three numbers")
            else:
                if (0 >= day["date"][0] or day["date"][0] > 12) or (0 >= day["date"][1] or day["date"][1] >= 5) or (
                        0 > day["date"][2] or day["date"][2] > 6):
                    raise FakeDayError(day["name"], False, reason="date", content="invalid date")
        for m in day["message"][:]:
            if not bool(m):
                day["message"].remove(m)
        if isinstance(day["message"], list) and len(day["message"]) == 0:
            raise FakeDayError(day["name"], False, reason="message", content="empty messages")
        else:
            if not bool(day["message"]):
                raise FakeDayError(day["name"], False, reason="message", content="empty messages")


def get_wish_day(server: PluginServerInterface) -> list:
    folder = server.get_data_folder()
    file = join(folder, "wish_days.json")
    if exists(file):
        with open(file, "r", encoding="utf8") as f:
            days = load(f)
        check_legitimacy(days)
        return days
    else:
        with open(file, "w", encoding="utf8") as f:
            dump(DEFAULT_WISH_DAYS, f, indent=4, ensure_ascii=False)
        return DEFAULT_WISH_DAYS


def get_wish_message(days: List[dict]) -> Union[Dict[str, str], None]:
    def _get_week(source_date: tuple, now_date: struct_time) -> bool:
        if source_date[0] != now_date[1]:
            return False
        first_week = int(m_date(now_date[0], now_date[1], 1).strftime("%W"))
        today_week = int(m_date(now_date[0],
                                now_date[1], now_date[2]).strftime("%W"))
        week = today_week - first_week + 1
        if source_date[1] != week:
            return False
        return True if source_date[2] == now_date[6] else False

    today: struct_time = localtime()
    lunar = LunarDate.today()
    lunar = (lunar.month, lunar.day)
    for day in days:
        date_type: str = day["type"]
        date: tuple = day["date"]
        message: Union[str, List[str]] = day["message"]
        if date_type == "Lunar" and date != lunar:
            continue
        elif date_type == "Solar" and date != today[1:3]:
            continue
        elif date_type == "Week" and not _get_week(date, today):
            continue
        return {
            "message": message[randint(0, len(message) - 1)]
            if isinstance(message, list) else message,
            "day": day["name"]
        }
    # Default:None, no action
