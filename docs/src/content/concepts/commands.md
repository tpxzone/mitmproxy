---
title: "命令"
weight: 6
aliases:
  - /concepts-commands/
---

# 命令 {#commands}

命令是让用户主动与插件交互的机制。最典型的例子大概就是 mitmproxy 的控制台用户界面——
这个工具里的每一次交互都是绑定到按键上的命令。命令也构成了一种灵活而强大的方式，
让你从命令提示符与 mitmproxy 交互。在 mitmproxy 控制台里，你可以用 `:` 键进入命令提示符。
提示符对命令名和许多内置参数类型都有智能 Tab 补全——试试看。

命令的权威参考是 `--commands` 参数，每个 mitmproxy 工具都暴露了它。传入该参数会把所有已
注册命令、它们的参数和返回值以带注解的列表形式打印到屏幕上。在 mitmproxy 控制台里，
你也可以在命令浏览器中查看所有命令的面板（默认通过 `C` 键绑定访问）。

# 使用 Flow {#working-with-flows}

mitmproxy 的许多命令都以 flow 作为参数。例如，客户端重放命令的签名是这样的：

```
replay.client [flow]
```

这意味着它期望接收一个或多个 flow 的序列。这就是[flow 规格]({{< relref
"/concepts/filters" >}})的用武之地——调用命令时，mitmproxy 会智能地把一种灵活的 flow
选择语言展开成一个 flow 列表。

启动 mitmproxy 控制台，抓一些流量，这样我们就有 flow 可以操作了。现在输入下面的命令：

```
:replay.client @focus
```

一定要试试对命令名和 flow 规格使用 Tab 补全。`@focus` 说明符会展开为当前聚焦的 flow，
所以你应该会看到这条 flow 被重放。不过，重放可以接受任意数量的 flow。试试下面的命令：

```
:replay.client @all
```

现在你应该会看到所有 flow 被逐条重放。这里我们可以用上 mitmproxy 过滤语言的全部能力，
所以比如说，我们也可以只重放某个特定域名的 flow：

```
:replay.client "~d google.com"
```

# 自定义按键绑定 {#custom-key-bindings}

mitmproxy 的按键绑定可以在 `~/.mitmproxy/keys.yaml` 文件中按你的需要定制。该文件由一系列
映射组成，可用的键如下：

* `key`（**必填**）：要绑定的按键。
* `cmd`（**必填**）：按下该键时要执行的命令。
* `context`：该按键应生效的上下文列表。默认是 **global**（即该键在任何地方都生效）。
  合法的上下文有 `chooser`、`commands`、`dataviewer`、`eventlog`、`flowlist`、`flowview`、
  `global`、`grideditor`、`help`、`keybindings`、`options`。
* `help`：该绑定的帮助文本，会显示在按键绑定浏览器里。

#### 示例 {#example}

{{< example src="examples/keys.yaml" lang="yaml" >}}
