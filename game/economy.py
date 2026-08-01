import random

TIER_THRESHOLDS = [
    ("青铜", 0),
    ("白银", 100),
    ("黄金", 300),
    ("铂金", 600),
    ("钻石", 1000),
    ("大师", 1500),
    ("传说", 2500),
]

ITEMS = {
    "hp_potion":       {"name": "生命药水", "desc": "恢复生命值", "price_gold": 50},
    "mp_potion":       {"name": "魔法药水", "desc": "恢复魔法值", "price_gold": 50},
    "map_scroll":      {"name": "地图卷轴", "desc": "揭示一个未探索区域", "price_gold": 100},
    "compass":         {"name": "指南针",   "desc": "跑图时指引正确方向", "price_gold": 80},
    "lucky_amulet":    {"name": "幸运护符", "desc": "增加掉落概率", "price_gold": 200, "price_gem": 5},
    "exp_boost":       {"name": "经验祝福", "desc": "获得双倍经验（1小时）", "price_gold": 150, "price_gem": 3},
    "dungeon_key":     {"name": "副本钥匙", "desc": "解锁特殊副本", "price_gem": 10},
    "teleport_stone":  {"name": "传送石",   "desc": "快速移动到已探索地点", "price_gold": 120, "price_gem": 2},
    "treasure_map":    {"name": "藏宝图",   "desc": "指引隐藏宝藏位置", "price_gold": 250, "price_gem": 8},
    "mystery_box":     {"name": "神秘宝箱", "desc": "随机获得稀有物品", "price_gold": 300, "price_gem": 15},
}

SHOP_ITEMS = [k for k in ITEMS]


def calc_tier(points: int) -> str:
    for tier, threshold in reversed(TIER_THRESHOLDS):
        if points >= threshold:
            return tier
    return "青铜"


def next_tier_points(points: int) -> int:
    for tier, threshold in TIER_THRESHOLDS:
        if points < threshold:
            return threshold - points
    return 0


def calc_level(exp: int) -> int:
    return max(1, int(exp ** 0.5))


def calc_exp_for_next_level(level: int) -> int:
    return (level + 1) ** 2


def roll_gem(chance_pct: int) -> int:
    return 1 if random.randint(1, 100) <= chance_pct else 0
