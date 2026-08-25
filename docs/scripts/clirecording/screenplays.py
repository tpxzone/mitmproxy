#!/usr/bin/env python3
from clidirector import CliDirector


def record_user_interface(d: CliDirector):
    tmux = d.start_session(width=120, height=36)
    window = tmux.attached_window

    d.start_recording("recordings/mitmproxy_user_interface.cast")
    d.message(
        "欢迎来到 mitmproxy 教程。本课我们讲解用户界面。"
    )
    d.pause(1)
    d.exec("mitmproxy")
    d.pause(3)

    d.message("这是 mitmproxy 的默认视图。")
    d.message("每有新请求进来，mitmproxy 就会往视图里添加一行。")
    d.message("我们在另一个终端里用 `curl` 生成一些请求。")

    pane_top = d.current_pane
    pane_bottom = window.split_window(attach=True)
    pane_bottom.resize_pane(height=12)

    d.focus_pane(pane_bottom)
    d.pause(2)

    d.type("curl")
    d.message("用 curl 的 `--proxy` 选项把 mitmproxy 配置为代理。")
    d.type(" --proxy http://127.0.0.1:8080")

    d.message("我们使用纯文本天气服务 `wttr.in`。")
    d.exec(' "http://wttr.in/Dunedin?0"')

    d.pause(2)
    d.press_key("Up")
    d.press_key("Left", count=3)
    d.press_key("BSpace", count=7)
    d.exec("Innsbruck")

    d.pause(2)
    d.exec("exit", target=pane_bottom)

    d.focus_pane(pane_top)

    d.message("你会在 flow 列表中看到发往 `wttr.in` 的请求。")

    d.message("mitmproxy 通过键盘快捷键来操作。")
    d.message("用方向键 `↑` 和 `↓` 来改变聚焦的 flow（`>>`）。")
    d.press_key("Down", pause=0.5)
    d.press_key("Up", pause=0.5)
    d.press_key("Down", pause=0.5)
    d.press_key("Up", pause=0.5)

    d.message("聚焦的 flow（`>>`）会被用作各种命令的作用目标。")

    d.message("其中一个命令用于显示 flow 详情，它绑定到 `ENTER`。")

    d.message("按 `ENTER` 查看聚焦 flow 的详情。")
    d.press_key("Enter")

    d.message("flow 详情视图有 3 个面板：请求、响应和详情。")
    d.message("用方向键 `←` 和 `→` 在面板之间切换。")
    d.press_key("Right", count=2, pause=2.5)
    d.press_key("Left", count=2, pause=1)

    d.message(
        "按 `q` 退出当前视图。",
    )
    d.type("q")

    d.message("按 `?` 获取所有可用键盘快捷键的列表。")
    d.type("?")
    d.pause(2)
    d.press_key("Down", count=20, pause=0.25)

    d.message("提示：记住 `?` 这个快捷键，它在每个视图里都能用。")
    d.message("按 `q` 退出当前视图。")
    d.type("q")

    d.message("每个快捷键在内部都绑定到一个命令。")
    d.message("你也可以直接执行命令（不用快捷键）。")
    d.message("按 `:` 打开底部的命令提示符。")
    d.type(":")

    d.message("输入 `console.view.flow @focus`。")
    d.type("console.view.flow @focus")

    d.message("命令 `console.view.flow` 会打开某条 flow 的详情视图。")

    d.message("参数 `@focus` 指定了目标 flow。")

    d.message("按 `ENTER` 执行该命令。")
    d.press_key("Enter")

    d.message(
        "命令能释放 mitmproxy 的全部威力，比如用来配置拦截。"
    )

    d.message("现在你已经了解 mitmproxy 界面的基础知识以及如何操作它了。")
    d.pause(1)

    d.message("在下一课中，你将学习如何拦截 flow。")
    d.save_instructions("recordings/mitmproxy_user_interface_instructions.json")
    d.end()


def record_intercept_requests(d: CliDirector):
    tmux = d.start_session(width=120, height=36)
    window = tmux.attached_window

    d.start_recording("recordings/mitmproxy_intercept_requests.cast")
    d.message(
        "欢迎来到 mitmproxy 教程。本课我们讲解请求拦截。"
    )
    d.pause(1)
    d.exec("mitmproxy")
    d.pause(3)

    d.message("我们首先需要配置 mitmproxy 来拦截请求。")

    d.message(
        "按 `i`，mitmproxy 的命令提示符会预填入 `set intercept ''`。"
    )
    d.type("i")
    d.pause(2)

    d.message(
        "我们用 flow 过滤表达式 `~u <regex>` 只拦截特定 URL。"
    )
    d.message(
        "此外，我们用过滤器 `~q` 只拦截请求，不拦截响应。"
    )
    d.message("我们用 `&` 把两个 flow 过滤器组合起来。")

    d.message(
        "在 `set intercept` 命令的引号之间输入 `~u /Dunedin & ~q`，然后按 `ENTER`。"
    )
    d.exec("~u /Dunedin & ~q")
    d.message("底部栏显示拦截已配置完成。")

    d.message("我们在另一个终端里用 `curl` 生成一个请求。")

    pane_top = d.current_pane
    pane_bottom = window.split_window(attach=True)
    pane_bottom.resize_pane(height=12)

    d.focus_pane(pane_bottom)
    d.pause(2)

    d.exec('curl --proxy http://127.0.0.1:8080 "http://wttr.in/Dunedin?0"')
    d.pause(2)

    d.focus_pane(pane_top)

    d.message("你会在 flow 列表中看到新增的一行。")
    d.message(
        "这条新 flow 显示为红色，表示它已被拦截。"
    )
    d.message(
        "把焦点（`>>`）放到被拦截的 flow 上。在我们的例子里它已经是聚焦状态了。"
    )
    d.message("按 `a` 不做任何修改直接放行这条 flow。")
    d.type("a")
    d.pause(2)

    d.focus_pane(pane_bottom)

    d.message("再提交一个请求，并把焦点放到它的 flow 上。")
    d.press_key("Up")
    d.press_key("Enter")
    d.pause(2)

    d.focus_pane(pane_top)
    d.press_key("Down")
    d.pause(1)

    d.message(
        "按 `X` 杀掉这条 flow，也就是把它丢弃，不转发到最终目的地 `wttr.in`。"
    )
    d.type("X")
    d.pause(3)

    d.message("在下一课中，你将学习如何修改被拦截的 flow。")
    d.save_instructions("recordings/mitmproxy_intercept_requests_instructions.json")
    d.end()


def record_modify_requests(d: CliDirector):
    tmux = d.start_session(width=120, height=36)
    window = tmux.attached_window

    d.start_recording("recordings/mitmproxy_modify_requests.cast")
    d.message(
        "欢迎来到 mitmproxy 教程。本课我们讲解如何修改被拦截的请求。"
    )
    d.pause(1)
    d.exec("mitmproxy")
    d.pause(3)

    d.message(
        "我们配置并使用与上一课相同的拦截规则。"
    )
    d.message(
        "按 `i` 预填 mitmproxy 的命令提示符，输入 flow 过滤器 `~u /Dunedin & ~q`，然后按 `ENTER`。"
    )
    d.type("i")
    d.pause(2)
    d.exec("~u /Dunedin & ~q")

    d.message("我们在另一个终端里用 `curl` 生成一个请求。")

    pane_top = d.current_pane
    pane_bottom = window.split_window(attach=True)
    pane_bottom.resize_pane(height=12)

    d.focus_pane(pane_bottom)
    d.pause(2)

    d.exec('curl --proxy http://127.0.0.1:8080 "http://wttr.in/Dunedin?0"')
    d.pause(2)

    d.focus_pane(pane_top)

    d.message("现在我们想修改这个被拦截的请求。")
    d.message(
        "把焦点（`>>`）放到被拦截的 flow 上。在我们的例子里它已经是聚焦状态了。"
    )

    d.message("按 `ENTER` 打开这条被拦截 flow 的详情视图。")
    d.press_key("Enter")

    d.message("按 `e` 编辑这条被拦截的 flow。")
    d.type("e")

    d.message("mitmproxy 会询问要修改哪一部分。")

    d.message("用方向键选中 `path`，然后按 `ENTER`。")
    d.press_key("Down", count=3, pause=0.5)
    d.pause(1)
    d.press_key("Enter")

    d.message(
        "mitmproxy 会逐行列出所有路径片段，在我们的例子里只有 `Dunedin`。"
    )
    d.message("按 `ENTER` 修改选中的路径片段。")
    d.press_key("Down", pause=2)
    d.press_key("Enter")

    d.message("把 `Dunedin` 替换为 `Innsbruck`。")
    d.press_key("BSpace", count=7, pause=0.5)
    d.type("Innsbruck", pause=0.5)

    d.message("按 `ESC` 确认你的修改。")
    d.press_key("Escape")

    d.message("按 `q` 返回 flow 详情视图。")
    d.type("q")

    d.message("按 `a` 放行这条被拦截的 flow。")
    d.type("a")
    d.pause(2)

    d.message(
        "你会看到请求 URL 已被修改，`wttr.in` 返回的是 `Innsbruck` 的天气预报。"
    )

    d.message("在下一课中，你将学习如何重放 flow。")
    d.save_instructions("recordings/mitmproxy_modify_requests_instructions.json")
    d.end()


def record_replay_requests(d: CliDirector):
    tmux = d.start_session(width=120, height=36)
    window = tmux.attached_window

    d.start_recording("recordings/mitmproxy_replay_requests.cast")
    d.message(
        "欢迎来到 mitmproxy 教程。本课我们讲解重放请求。"
    )
    d.pause(1)
    d.exec("mitmproxy")
    d.pause(3)

    d.message(
        "我们先生成一个可以用来重放的请求。在另一个终端里用 `curl`。"
    )

    pane_top = d.current_pane
    pane_bottom = window.split_window(attach=True)
    pane_bottom.resize_pane(height=12)

    d.focus_pane(pane_bottom)
    d.pause(2)

    d.exec('curl --proxy http://127.0.0.1:8080 "http://wttr.in/Dunedin?0"')
    d.pause(2)

    d.focus_pane(pane_top)

    d.message("现在我们想重放这个请求。")
    d.message(
        "把焦点（`>>`）放到要重放的那个请求上。在我们的例子里它已经是聚焦状态了。"
    )
    d.message("按 `r` 重放该请求。")
    d.type("r")

    d.message(
        "注意重放的 flow 不会新增行，而是更新已有的那一行。"
    )
    d.message(
        "每按一次 `r`，mitmproxy 就会把这个请求再发给服务器一次，并更新该 flow。"
    )
    d.press_key("r", count=4, pause=1)

    d.message("你也可以在重放之前先修改一条 flow。")
    d.message("做法和上一课演示的一样，按 `e` 即可。")

    d.message(
        "恭喜！你已经完成了 mitmproxy 教程的所有课程。"
    )
    d.save_instructions("recordings/mitmproxy_replay_requests_instructions.json")
    d.end()
