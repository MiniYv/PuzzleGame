import random
import math

DUNGEONS = [
    {"id": "d1", "name": "废弃矿坑", "desc": "被遗弃的矿坑中传来诡异声响", "difficulty": 1, "puzzles": 3},
    {"id": "d2", "name": "幽暗森林", "desc": "密林深处隐藏着上古遗迹", "difficulty": 1, "puzzles": 3},
    {"id": "d3", "name": "古老神殿", "desc": "失落的文明留下的最后痕迹", "difficulty": 2, "puzzles": 4},
    {"id": "d4", "name": "冰封洞穴", "desc": "永冻之地深处的冰晶迷宫", "difficulty": 2, "puzzles": 4},
    {"id": "d5", "name": "火焰山谷", "desc": "活火山内部的高温炼狱", "difficulty": 3, "puzzles": 5},
    {"id": "d6", "name": "暗影城堡", "desc": "被黑暗笼罩的古堡", "difficulty": 3, "puzzles": 5},
    {"id": "d7", "name": "天空之塔", "desc": "直入云霄的魔法高塔", "difficulty": 4, "puzzles": 6},
    {"id": "d8", "name": "深海遗迹", "desc": "沉没在海底的远古都市", "difficulty": 4, "puzzles": 6},
    {"id": "d9", "name": "龙之巢穴", "desc": "远古巨龙沉睡之处", "difficulty": 5, "puzzles": 7},
    {"id": "d10", "name": "虚空之门", "desc": "连通异次元的终极挑战", "difficulty": 5, "puzzles": 8},
]

DUNGEON_MAP = {d["id"]: d for d in DUNGEONS}

PUZZLE_POOL = [
    {"question": "什么东西越洗越脏？", "answer": "水", "hint": "常见的液体"},
    {"question": "什么东西有头无脚？", "answer": "针", "hint": "缝纫用品"},
    {"question": "什么东西越削越大？", "answer": "洞", "hint": "在地上挖的"},
    {"question": "什么东西能倒立不倒？", "answer": "不倒翁", "hint": "一个玩具"},
    {"question": "什么东西长在山上却比山高？", "answer": "山顶的树", "hint": "植物"},
    {"question": "什么东西越烧越旺？", "answer": "火", "hint": "自然元素"},
    {"question": "什么东西有口不能说话？", "answer": "茶壶", "hint": "厨房用品"},
    {"question": "什么东西有耳不能听？", "answer": "花瓶", "hint": "装饰品"},
    {"question": "什么东西有脚不能走路？", "answer": "桌子", "hint": "家具"},
    {"question": "什么东西越洗越小？", "answer": "肥皂", "hint": "清洁用品"},
    {"question": "什么东西看不见摸不着但很重要？", "answer": "空气", "hint": "看不见的气体"},
    {"question": "什么东西越老越值钱？", "answer": "古董", "hint": "收藏品"},
    {"question": "什么东西越吃越饿？", "answer": "火", "hint": "自然元素"},
    {"question": "什么东西越走越近却永远到不了？", "answer": "地平线", "hint": "天地交界"},
    {"question": "什么东西没有嘴却能说话？", "answer": "回声", "hint": "山谷里的声音"},
    {"question": "什么东西越分越多？", "answer": "知识", "hint": "学习的东西"},
    {"question": "什么东西越少越珍贵？", "answer": "时间", "hint": "不可逆的"},
    {"question": "什么东西越藏越显眼？", "answer": "太阳", "hint": "天上的"},
    {"question": "什么东西越看越小？", "answer": "星星", "hint": "夜晚天上"},
    {"question": "什么东西来了就不走？", "answer": "影子", "hint": "光与身体"},
    {"question": "什么东西越想越复杂？", "answer": "问题", "hint": "待解决的"},
    {"question": "什么东西越简单越难？", "answer": "选择", "hint": "决策"},
    {"question": "什么东西越熟悉越陌生？", "answer": "自己", "hint": "反身代词"},
    {"question": "什么东西越平静越危险？", "answer": "水面", "hint": "水下可能暗流汹涌"},
    {"question": "什么东西越旧越有价值？", "answer": "历史", "hint": "过去的记录"},
    {"question": "什么东西越看越不清楚？", "answer": "迷雾", "hint": "天气现象"},
    {"question": "什么东西越走越远却始终在原点？", "answer": "跑步机", "hint": "健身器材"},
    {"question": "什么东西越翻越乱？", "answer": "回忆", "hint": "过去的事"},
    {"question": "什么东西越堆越高却不重？", "answer": "雪花", "hint": "冬天的"},
    {"question": "什么东西越多越看不清？", "answer": "人群", "hint": "很多人"},
    {"question": "什么东西越想越红？", "answer": "脸", "hint": "害羞时会"},
    {"question": "什么东西越多越安静？", "answer": "雪", "hint": "冬天的白色"},
    {"question": "什么东西有城有国却没有人家？", "answer": "棋盘", "hint": "游戏用品"},
    {"question": "什么东西有海有河却没有水？", "answer": "地图", "hint": "纸质"},
    {"question": "什么东西有山有谷却没有树？", "answer": "沙盘", "hint": "模型"},
    {"question": "什么东西有桥有路却没有车？", "answer": "画", "hint": "艺术作品"},
    {"question": "什么东西有门有窗却没有房子？", "answer": "相框", "hint": "装照片的"},
    {"question": "什么东西有手有脚却没有身体？", "answer": "手套袜子", "hint": "穿戴用品"},
    {"question": "什么东西有头有尾却没有身体？", "answer": "硬币", "hint": "钱币"},
    {"question": "什么东西越飞越远却从不消失？", "answer": "风筝", "hint": "线牵着"},
]


def generate_puzzles(count: int) -> list:
    return random.sample(PUZZLE_POOL, min(count, len(PUZZLE_POOL)))


def calc_dungeon_stars(correct: int, total: int) -> int:
    ratio = correct / total if total > 0 else 0
    if ratio >= 0.9:
        return 3
    elif ratio >= 0.7:
        return 2
    else:
        return 1


def calc_dungeon_rewards(dungeon_id: str, stars: int, config: dict) -> dict:
    dungeon = DUNGEON_MAP.get(dungeon_id, DUNGEONS[0])
    base_gold = config.get("dungeon_gold_reward", 30)
    base_gem = config.get("dungeon_gem_reward", 2)
    points = config.get("rank_points_per_dungeon", 20)
    multiplier = 1 + (stars - 1) * 0.5
    gold = int(base_gold * dungeon["difficulty"] * multiplier)
    gem = int(base_gem * dungeon["difficulty"] * multiplier)
    exp = int(10 * dungeon["difficulty"] * multiplier)
    return {"gold": gold, "gem": gem, "points": points, "exp": exp}


EXPLORE_EVENTS = [
    {"type": "discover", "text": "你发现了一处隐秘的遗迹！", "gold": 20, "exp": 10},
    {"type": "combat", "text": "遭遇了野生的怪物，经过一番战斗", "gold": 15, "exp": 15, "damage": 10},
    {"type": "treasure", "text": "找到了一个宝箱！", "gold": 50, "gem": 1, "exp": 20},
    {"type": "trap", "text": "触发了古老的陷阱", "damage": 20, "exp": 5},
    {"type": "rest", "text": "找到一处安全的地方休息", "hp_restore": 30, "exp": 5},
    {"type": "puzzle", "text": "发现了一道谜题石碑", "gold": 30, "exp": 15},
    {"type": "merchant", "text": "遇到了一位流浪商人", "gold": -20, "item": "map_scroll"},
    {"type": "viewpoint", "text": "登上了高处，美景尽收眼底", "exp": 10},
    {"type": "rain", "text": "突然下起了大雨", "damage": 5},
    {"type": "reward", "text": "被当地人热情款待", "gold": 25, "exp": 15, "hp_restore": 20},
]


def display_name(player, sender_id):
    nickname = player.get("nickname") if player else ""
    if nickname:
        return nickname
    sid = str(sender_id)
    return f"****{sid[-4:]}" if len(sid) > 4 else sid


def roll_explore_event():
    return random.choice(EXPLORE_EVENTS)


def apply_player_hp(max_hp: int, event: dict) -> int:
    damage = event.get("damage", 0)
    restore = event.get("hp_restore", 0)
    return max_hp - damage + restore
