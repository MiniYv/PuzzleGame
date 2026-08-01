from graci import on_command, plugin_handler, PluginContext
from ..database.db import ensure_player, get_player, get_leaderboard, get_rank
from ..game.core import display_name
from ..game.economy import calc_tier


@on_command("/排行")
@plugin_handler
async def handle_leaderboard(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    _text = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    args = _text.split()
    sort_by = "exp"
    title = "经验"
    if args:
        t = args[0]
        if t in ("金币", "gold"):
            sort_by = "gold"
            title = "金币"
        elif t in ("宝石", "gem"):
            sort_by = "gem"
            title = "宝石"
        elif t in ("经验", "exp", "等级"):
            sort_by = "exp"
            title = "经验"
        elif t in ("积分", "rank", "段位"):
            sort_by = "rank_points"
            title = "段位积分"
    rows = await get_leaderboard(sort_by)
    if not rows:
        await ctx.reply("暂无排行数据")
        return
    msg = f"【{title}排行榜】\n"
    for i, r in enumerate(rows):
        rank = i + 1
        medal = f"[{rank}]"
        name = display_name(r, r["player_id"])
        if sort_by == "rank_points":
            tier = calc_tier(r["rank_points"])
            msg += f"{medal} {name} - {r['rank_points']}分（{tier}）\n"
        else:
            msg += f"{medal} {name} - {r[sort_by]}\n"
    my_rank = await get_rank(pid, sort_by)
    player = await get_player(pid)
    if player and my_rank:
        msg += f"\n你的排名：第{my_rank}名"
    msg += f"\n（你的标识：{display_name(player, pid)}）"
    await ctx.reply(msg)
