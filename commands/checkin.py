from graci import on_command, plugin_handler, PluginContext, config_manager
from ..database.db import ensure_player, get_player, update_player, has_checkin_today, mark_checkin
from ..game.economy import roll_gem

PLUGIN_NAME = "解谜游戏"


@on_command("/签到")
@plugin_handler
async def handle_checkin(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    if await has_checkin_today(pid):
        await ctx.reply("你今天已经签到过了，明天再来吧！")
        return
    cfg = config_manager.get_plugin(PLUGIN_NAME)
    gold = cfg.get("daily_checkin_gold", 50)
    gem_chance = cfg.get("daily_checkin_gem_chance", 10)
    player = await get_player(pid)
    new_gold = (player.get("gold") or 0) + gold
    await update_player(pid, gold=new_gold)
    await mark_checkin(pid)
    msg = f"签到成功！获得 {gold} 金币"
    gem = roll_gem(gem_chance)
    if gem:
        new_gem = (player.get("gem") or 0) + gem
        await update_player(pid, gem=new_gem)
        msg += f" 和 {gem} 宝石"
    await ctx.reply(msg)
