"""解谜游戏 — 包含副本、跑图、排行榜、签到、双货币、背包系统"""
import os
from graci import get_logger, on_command, plugin_handler, PluginContext, config_manager, get_plugin_data_dir

logger = get_logger("PuzzleGame")

config_manager.register_plugin_config("解谜游戏")

DATA_DIR = get_plugin_data_dir("PuzzleGame")


@on_command("/谜题", "/puzzle")
@plugin_handler
async def handle_puzzle(ctx: PluginContext):
    await ctx.reply(
        "【解谜游戏】可用指令：\n"
        "/签到 - 每日签到领金币\n"
        "/副本 - 挑战解谜副本\n"
        "/跑图 - 探索世界地图\n"
        "/地图 - 查看地图信息\n"
        "/排行 - 查看排行榜\n"
        "/商店 - 购买道具\n"
        "/背包 - 查看道具\n"
        "/使用 <道具> - 使用道具\n"
        "/改名 <昵称> - 设置昵称\n"
        "/我的 - 查看个人信息\n"
        "/谜题 - 显示本帮助"
    )
