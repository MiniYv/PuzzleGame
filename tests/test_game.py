"""Tests for PuzzleGame plugin core logic."""
import sys
import os

plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if plugin_dir not in sys.path:
    sys.path.insert(0, plugin_dir)

from game.economy import calc_tier, calc_level, roll_gem, TIER_THRESHOLDS, ITEMS, SHOP_ITEMS
from game.core import (
    DUNGEONS, DUNGEON_MAP, generate_puzzles,
    calc_dungeon_stars, calc_dungeon_rewards, PUZZLE_POOL,
    EXPLORE_EVENTS, roll_explore_event,
)
from data.countries import COUNTRIES, COUNTRY_MAP
from data.forbidden_zones import FORBIDDEN_ZONES


class TestEconomy:
    def test_tier_thresholds(self):
        assert TIER_THRESHOLDS[0] == ("青铜", 0)
        assert TIER_THRESHOLDS[-1] == ("传说", 2500)
        assert len(TIER_THRESHOLDS) == 7

    def test_calc_tier(self):
        assert calc_tier(0) == "青铜"
        assert calc_tier(50) == "青铜"
        assert calc_tier(100) == "白银"
        assert calc_tier(300) == "黄金"
        assert calc_tier(600) == "铂金"
        assert calc_tier(1000) == "钻石"
        assert calc_tier(1500) == "大师"
        assert calc_tier(2500) == "传说"
        assert calc_tier(5000) == "传说"

    def test_calc_level(self):
        assert calc_level(0) == 1
        assert calc_level(1) == 1
        assert calc_level(4) == 2
        assert calc_level(9) == 3

    def test_roll_gem(self):
        count_yes = sum(roll_gem(100) for _ in range(100))
        assert count_yes == 100
        count_no = sum(roll_gem(0) for _ in range(100))
        assert count_no == 0

    def test_shop_items_defined(self):
        for item_id in SHOP_ITEMS:
            assert item_id in ITEMS
            assert "name" in ITEMS[item_id]
            assert "desc" in ITEMS[item_id]
            assert "price_gold" in ITEMS[item_id] or "price_gem" in ITEMS[item_id]


class TestCore:
    def test_dungeons_count(self):
        assert len(DUNGEONS) >= 8

    def test_dungeon_map(self):
        for d in DUNGEONS:
            assert d["id"] in DUNGEON_MAP
            assert d["id"].startswith("d")
            assert d["difficulty"] >= 1
            assert d["puzzles"] >= 3

    def test_generate_puzzles(self):
        puzzles = generate_puzzles(3)
        assert len(puzzles) == 3
        for p in puzzles:
            assert "question" in p
            assert "answer" in p
            assert "hint" in p

    def test_generate_puzzles_max(self):
        many = generate_puzzles(100)
        assert len(many) <= len(PUZZLE_POOL)

    def test_calc_stars(self):
        assert calc_dungeon_stars(3, 3) == 3
        assert calc_dungeon_stars(2, 3) == 1
        assert calc_dungeon_stars(1, 3) == 1

    def test_calc_rewards(self):
        config = {"dungeon_gold_reward": 30, "dungeon_gem_reward": 2, "rank_points_per_dungeon": 20}
        rewards = calc_dungeon_rewards("d1", 3, config)
        assert rewards["gold"] > 0
        assert rewards["gem"] > 0
        assert rewards["points"] > 0
        assert rewards["exp"] > 0

    def test_explore_events(self):
        assert len(EXPLORE_EVENTS) >= 5
        event = roll_explore_event()
        assert "type" in event
        assert "text" in event

    def test_puzzle_pool(self):
        assert len(PUZZLE_POOL) >= 20


class TestMapData:
    def test_countries_count(self):
        assert len(COUNTRIES) == 7

    def test_each_country_has_20_plus_locations(self):
        for country in COUNTRIES:
            assert len(country["locations"]) >= 20, f"{country['name']} 只有 {len(country['locations'])} 个地点"

    def test_country_map(self):
        for country in COUNTRIES:
            assert country["name"] in COUNTRY_MAP

    def test_forbidden_zones(self):
        assert len(FORBIDDEN_ZONES) >= 3
