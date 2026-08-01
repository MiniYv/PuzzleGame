import random
from graci import on_command, plugin_handler, PluginContext, config_manager
from ..data.countries import COUNTRIES, COUNTRY_MAP
from ..data.forbidden_zones import FORBIDDEN_ZONES
from ..game.core import roll_explore_event, apply_player_hp
from ..game.economy import ITEMS
from ..database.db import (
    ensure_player, get_player, update_player, add_item,
    get_explored_locations, mark_location_discovered,
)

PLUGIN_NAME = "解谜游戏"

_player_hp = {}


@on_command("/跑图")
@plugin_handler
async def handle_explore(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    _text = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    args = _text.split()
    if not args:
        msg = "可探索的国家：\n"
        for c in COUNTRIES:
            msg += f"  {c['name']} - {c['desc']}\n"
        msg += "\n禁区（危险）：\n"
        for z in FORBIDDEN_ZONES:
            msg += f"  {z['name']}（危险等级{z['danger_level']}）\n"
        msg += "\n输入 /跑图 <国家名> 开始探索"
        await ctx.reply(msg)
        return
    country_name = args[0]
    country = COUNTRY_MAP.get(country_name)
    if not country:
        forbidden = {z["name"]: z for z in FORBIDDEN_ZONES}
        zone = forbidden.get(country_name)
        if zone:
            await ctx.reply(
                f"【{zone['name']}】{zone['desc']}\n"
                f"危险等级：{'!' * zone['danger_level']}\n"
                "禁区极度危险，暂未开放探索"
            )
            return
        await ctx.reply(f"未知地区：{country_name}。输入 /跑图 查看可探索国家")
        return
    explored = await get_explored_locations(pid)
    all_locs = country["locations"]
    unexplored = [l for l in all_locs if l not in explored]
    if not unexplored:
        await ctx.reply(f"你已探索完{country_name}全部地区！")
        return
    target = random.choice(unexplored)
    event = roll_explore_event()
    cfg = config_manager.get_plugin(PLUGIN_NAME)
    base_gold = cfg.get("explore_gold_base", 10)
    gold = event.get("gold", 0) + base_gold
    gem = event.get("gem", 0)
    exp = event.get("exp", 0)
    _player_hp.setdefault(pid, 100)
    _player_hp[pid] = apply_player_hp(_player_hp[pid], event)
    player = await get_player(pid)
    new_gold = (player.get("gold") or 0) + gold
    new_exp = (player.get("exp") or 0) + exp
    await update_player(pid, gold=new_gold, exp=new_exp)
    if gem:
        new_gem = (player.get("gem") or 0) + gem
        await update_player(pid, gem=new_gem)
    await mark_location_discovered(pid, country_name, target)
    if "item" in event:
        await add_item(pid, event["item"])
    msg = f"你来到了【{target}】\n"
    msg += f"{event['text']}\n"
    if event.get("damage", 0) > 0:
        msg += f"受到 {event['damage']} 点伤害，剩余HP：{max(0, _player_hp[pid])}\n"
    if event.get("hp_restore", 0) > 0:
        msg += f"恢复 {event['hp_restore']} 点生命，当前HP：{_player_hp[pid]}\n"
    rewards = []
    if gold:
        rewards.append(f"{gold}金币")
    if gem:
        rewards.append(f"{gem}宝石")
    if exp:
        rewards.append(f"{exp}经验")
    if "item" in event:
        item_name = ITEMS.get(event["item"], {}).get("name", event["item"])
        rewards.append(f"获得道具【{item_name}】")
    if rewards:
        msg += "获得：" + " ".join(rewards)
    discovered = len(explored) + 1
    total = len(all_locs)
    msg += f"\n{country_name}探索进度：{discovered}/{total}"
    await ctx.reply(msg)


@on_command("/地图")
@plugin_handler
async def handle_map(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    _text = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    args = _text.split()
    if not args:
        msg = "世界地图：\n"
        for c in COUNTRIES:
            msg += f"  {c['name']}（{len(c['locations'])}个地点）\n"
        msg += "\n输入 /地图 <国家名> 查看详细"
        await ctx.reply(msg)
        return
    country_name = " ".join(args)
    country = COUNTRY_MAP.get(country_name)
    if not country:
        await ctx.reply(f"未知国家：{country_name}。输入 /地图 查看国家列表")
        return
    explored = await get_explored_locations(pid)
    msg = f"【{country['name']}】\n{country['desc']}\n\n地点列表：\n"
    for loc in country["locations"]:
        icon = "✓" if loc in explored else "○"
        msg += f"  {icon} {loc}\n"
    total = len(country["locations"])
    discovered = sum(1 for l in country["locations"] if l in explored)
    msg += f"\n探索进度：{discovered}/{total}"
    await ctx.reply(msg)
