from graci import on_command, plugin_handler, PluginContext, config_manager
from ..game.core import DUNGEONS, DUNGEON_MAP, generate_puzzles, calc_dungeon_stars, calc_dungeon_rewards
from ..database.db import ensure_player, get_player, update_player, get_dungeon_progress, complete_dungeon
from ..game.economy import calc_tier

PLUGIN_NAME = "解谜游戏"

_player_sessions = {}


@on_command("/副本")
@plugin_handler
async def handle_dungeon(ctx: PluginContext):
    pid = ctx.sender_id
    await ensure_player(pid)
    _text = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    args = _text.split()
    if not args:
        lines = ["可挑战的副本："]
        progress = await get_dungeon_progress(pid)
        for d in DUNGEONS:
            p = progress.get(d["id"], {})
            done = p.get("completed", 0)
            stars = p.get("stars", 0)
            star_str = "★" * stars + "☆" * (3 - stars) if done else "未挑战"
            lines.append(f"  {d['id']} {d['name']} [难度{d['difficulty']}] {star_str}")
        lines.append("输入 /副本 <副本ID> 开始挑战")
        await ctx.reply("\n".join(lines))
        return
    dungeon_id = args[0]
    dungeon = DUNGEON_MAP.get(dungeon_id)
    if not dungeon:
        await ctx.reply(f"未知副本: {dungeon_id}，输入 /副本 查看列表")
        return
    puzzles = generate_puzzles(dungeon["puzzles"])
    _player_sessions[pid] = {
        "dungeon_id": dungeon_id,
        "puzzles": puzzles,
        "index": 0,
        "correct": 0,
        "total": len(puzzles),
    }
    first = puzzles[0]
    await ctx.reply(
        f"开始挑战【{dungeon['name']}】\n"
        f"共 {len(puzzles)} 道谜题，请回答以下问题：\n"
        f"第1题：{first['question']}\n"
        f"（提示：{first['hint']}）\n输入 /答 <答案> 回答"
    )


@on_command("/答")
@plugin_handler
async def handle_answer(ctx: PluginContext):
    pid = ctx.sender_id
    session = _player_sessions.get(pid)
    if not session:
        await ctx.reply("你没有正在进行的副本，输入 /副本 开始挑战")
        return
    answer = ctx.raw_text.replace(ctx.command, "", 1).strip() if ctx.command else ctx.raw_text
    if not answer:
        await ctx.reply("请输入答案，如：/答 水")
        return
    puzzles = session["puzzles"]
    idx = session["index"]
    puzzle = puzzles[idx]
    is_correct = answer.lower() == puzzle["answer"].lower()
    if is_correct:
        session["correct"] += 1
    session["index"] += 1
    if session["index"] >= session["total"]:
        correct = session["correct"]
        total = session["total"]
        stars = calc_dungeon_stars(correct, total)
        cfg = config_manager.get_plugin(PLUGIN_NAME)
        rewards = calc_dungeon_rewards(session["dungeon_id"], stars, cfg)
        player = await get_player(pid)
        new_gold = (player.get("gold") or 0) + rewards["gold"]
        new_gem = (player.get("gem") or 0) + rewards["gem"]
        new_exp = (player.get("exp") or 0) + rewards["exp"]
        new_points = (player.get("rank_points") or 0) + rewards["points"]
        new_tier = calc_tier(new_points)
        await update_player(pid, gold=new_gold, gem=new_gem, exp=new_exp, rank_points=new_points, rank_tier=new_tier)
        await complete_dungeon(pid, session["dungeon_id"], stars)
        del _player_sessions[pid]
        await ctx.reply(
            f"副本完成！答对 {correct}/{total}\n"
            f"评价：{'★' * stars}{'☆' * (3 - stars)}\n"
            f"获得：{rewards['gold']}金币 {rewards['gem']}宝石 {rewards['exp']}经验\n"
            f"段位积分 +{rewards['points']}，当前段位：{new_tier}"
        )
    else:
        next_puzzle = puzzles[session["index"]]
        await ctx.reply(
            f"{'回答正确！' if is_correct else '回答错误，继续努力！'}\n"
            f"第{session['index'] + 1}题：{next_puzzle['question']}\n"
            f"（提示：{next_puzzle['hint']}）"
        )
