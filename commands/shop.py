import random
from graci import on_command, plugin_handler, PluginContext, config_manager
from ..database.db import ensure_player, get_player, update_player, get_inventory, add_item, remove_item, get_rank
from ..game.economy import ITEMS, SHOP_ITEMS, calc_tier, calc_level
from ..game.core import display_name
from ..data.countries import COUNTRIES

PLUGIN_NAME = "解谜游戏"


@on_command("/背包")
@plugin_handler
async def handle_inventory(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    inv = await get_inventory(pid)
    if not inv:
        await ctx.reply("背包是空的，去商店购买一些道具吧！")
        return
    msg = "【背包】\n"
    for item_id, qty in inv.items():
        info = ITEMS.get(item_id, {})
        name = info.get("name", item_id)
        msg += f"  {name} x{qty}\n"
    await ctx.reply(msg)


@on_command("/商店")
@plugin_handler
async def handle_shop(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    _text = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    args = _text.split()
    if not args:
        msg = "【商店】\n"
        for i, item_id in enumerate(SHOP_ITEMS, 1):
            info = ITEMS[item_id]
            parts = []
            if "price_gold" in info:
                parts.append(f"{info['price_gold']}金币")
            if "price_gem" in info:
                parts.append(f"{info['price_gem']}宝石")
            price = " / ".join(parts)
            msg += f"  {i}. {info['name']} - {price}\n"
            msg += f"     {info['desc']}\n"
        msg += "\n输入 /商店 购买 <道具名> 购买道具"
        await ctx.reply(msg)
        return
    if args[0] == "购买" and len(args) >= 2:
        item_name = " ".join(args[1:])
        target_id = None
        for item_id, info in ITEMS.items():
            if info["name"] == item_name:
                target_id = item_id
                break
        if not target_id:
            await ctx.reply(f"未知道具：{item_name}，输入 /商店 查看列表")
            return
        info = ITEMS[target_id]
        player = await get_player(pid)
        gold = player.get("gold") or 0
        gem = player.get("gem") or 0
        price_gold = info.get("price_gold", 0)
        price_gem = info.get("price_gem", 0)
        if price_gold > 0 and gold < price_gold:
            await ctx.reply(f"金币不足！需要{price_gold}金币，当前{gold}金币")
            return
        if price_gem > 0 and gem < price_gem:
            await ctx.reply(f"宝石不足！需要{price_gem}宝石，当前{gem}宝石")
            return
        new_gold = gold - price_gold
        new_gem = gem - price_gem
        await update_player(pid, gold=new_gold, gem=new_gem)
        await add_item(pid, target_id)
        cost_parts = []
        if price_gold:
            cost_parts.append(f"{price_gold}金币")
        if price_gem:
            cost_parts.append(f"{price_gem}宝石")
        await ctx.reply(f"成功购买【{info['name']}】！花费{' / '.join(cost_parts)}")
        return
    await ctx.reply("格式错误。输入 /商店 查看商品，/商店 购买 <道具名> 购买")


@on_command("/使用")
@plugin_handler
async def handle_use(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    item_name = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    if not item_name:
        await ctx.reply("输入 /使用 <道具名> 使用道具")
        return
    target_id = None
    for item_id, info in ITEMS.items():
        if info["name"] == item_name:
            target_id = item_id
            break
    if not target_id:
        await ctx.reply(f"未知道具：{item_name}")
        return
    ok = await remove_item(pid, target_id)
    if not ok:
        await ctx.reply(f"背包中没有【{item_name}】")
        return
    if target_id == "hp_potion":
        await ctx.reply("使用了生命药水，恢复50点生命值！")
    elif target_id == "mp_potion":
        await ctx.reply("使用了魔法药水，恢复30点魔法值！")
    elif target_id == "map_scroll":
        all_locs = []
        for c in COUNTRIES:
            all_locs.extend(c["locations"])
        random_loc = random.choice(all_locs)
        from ..database.db import mark_location_discovered
        await mark_location_discovered(pid, "未知", random_loc)
        await ctx.reply(f"地图揭示了新地点：{random_loc}！")
    elif target_id == "lucky_amulet":
        await ctx.reply("幸运护符已激活，下次探索将有更好的收获！")
    elif target_id == "mystery_box":
        rewards = ["hp_potion", "mp_potion", "dungeon_key", "treasure_map"]
        reward = random.choice(rewards)
        await add_item(pid, reward)
        reward_name = ITEMS[reward]["name"]
        await ctx.reply(f"打开神秘宝箱，获得【{reward_name}】！")
    else:
        await ctx.reply(f"使用了【{item_name}】！")


@on_command("/改名")
@plugin_handler
async def handle_rename(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    new_name = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    if not new_name or len(new_name) > 20:
        await ctx.reply("昵称不能为空且不超过20字，格式：/改名 <新昵称>")
        return
    await update_player(pid, nickname=new_name)
    await ctx.reply(f"昵称已修改为：{new_name}")


@on_command("/我的")
@plugin_handler
async def handle_profile(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    player = await get_player(pid)
    if not player:
        await ctx.reply("尚未注册，请先使用任意游戏指令自动注册")
        return
    name = display_name(player, pid)
    tier = calc_tier(player.get("rank_points") or 0)
    level = calc_level(player.get("exp") or 0)
    my_rank = await get_rank(pid, "exp")
    msg = (
        f"【{name}的个人信息】\n"
        f"等级：{level}\n"
        f"金币：{player.get('gold', 0)}\n"
        f"宝石：{player.get('gem', 0)}\n"
        f"段位：{tier}（积分：{player.get('rank_points', 0)}）\n"
        f"经验：{player.get('exp', 0)}\n"
        f"排名：第{my_rank}名\n"
        f"上次签到：{player.get('last_checkin') or '未签到'}"
    )
    await ctx.reply(msg)
