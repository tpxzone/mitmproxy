---
title: "自定义命令"
weight: 4
aliases:
    - /addons-commands/
---

# 命令 {#commands}

命令让用户可以主动与插件交互——查询其状态、指挥它执行动作，以及让它转换数据。和
[选项]({{< relref "/addons/options" >}})一样，命令是带类型的，调用方式和命令返回的数据
都会在运行时被检查。命令是一种非常强大的构造——例如，mitmproxy 控制台中的所有用户交互
都是通过把命令绑定到按键构建出来的。

## 简单示例 {#simple-example}

先从一个简单的例子开始。

{{< example src="examples/addons/commands-simple.py" lang="py" >}}

要看这个例子的实际效果，请加载该插件启动 mitmproxy 控制台：

```bash
> mitmproxy -s ./examples/addons/commands-simple.py
```

现在，确保事件日志是显示状态，然后在提示符下（输入 ":" 进入）执行命令：

```
:myaddon.inc
```

注意 Tab 补全也是可用的——我们插件的命令与内置命令完全平权。关于这个例子有几点需要说明：

- 命令通过 `command.command` 装饰器声明。每个命令都有一个唯一的名字——按约定，我们使用
  以英文句点分隔的名字，并以插件名作为前缀。
- 给命令加类型注解是强制的，包括返回类型（本例中是 `None`）。这让 mitmproxy 能够在整套
  工具中支持插件命令——运行时调用会做类型检查、插件命令会被纳入内置帮助、mitmproxy 控制台
  中的命令编辑器可以做复杂的补全和错误检查，等等。

## 使用 flow {#working-with-flows}

由于命令参数是带类型的，我们可以为处理某些重要数据类型提供特别的便利。其中最有用的是代表
mitmproxy 流量的 `Flows` 系列类型。

看看下面这个插件：

{{< example src="examples/addons/commands-flows.py" lang="py" >}}

`myaddon.addheader` 命令相当简单：它接收一个 flow 序列，然后给每个请求添加一个头部。
这个例子真正有趣的地方在于用户如何指定 flow。因为 mitmproxy 可以检查类型签名，
它能透明地帮我们把一个文本形式的 flow 选择器展开成一个 flow 序列。这意味着用户可以用上
[flow 过滤器]({{< relref "/concepts/filters" >}})的全部灵活性。我们来试试。

先把插件加载到 mitmproxy 里，并发一些流量过去，这样我们就有 flow 可以操作了：

```bash
> mitmproxy -s ./examples/addons/commands-flows.py
```

现在我们可以用多种方式调用这个玩具命令。先只对当前聚焦的 flow 执行它：

```
:myaddon.addheader @focus
```

也可以对所有 flow 执行：

```
:myaddon.addheader @all
```

或者只对来自 **google.com** 的 flow 执行：

```
:myaddon.addheader ~d google.com
```

更进一步，如果我们打算经常使用这些命令，可以轻而易举地在 mitmproxy 中把它们绑定到键盘
快捷键上。flow 选择器与命令结合起来威力惊人，让我们能够构建并暴露可复用的函数来操作 flow。

## 路径 {#paths}

命令可以接受任意数量的参数。我们在前一个例子的基础上继续说明这一点，同时演示另一个特殊
类型：路径。

{{< example src="examples/addons/commands-paths.py" lang="py" >}}

我们的命令会统计指定 flow 集合中各域名的直方图，并把它写入一个路径，该路径是命令的第二个
参数。试着这样调用它：

```
:myaddon.histogram @all /tmp/xxx
```

注意 mitmproxy 对 flow 规格和路径都提供了 Tab 补全。

## 支持的类型 {#supported-types}

选项支持下列类型。如果你需要用到这里没列出的类型，请给我们发 pull request。

- 基本类型：`str`、`int`、`bool`
- 序列：`typing.Sequence[str]`
- flow 及 flow 序列：`flow.Flow` 和 `typing.Sequence[flow.Flow]`
- 多选字符串：`types.Choice`
- 元类型：`types.Command` 和 `types.Arg`。它们用于构造调用其他命令的命令，
  在按键绑定中最为常用——mitmproxy 控制台内置的按键绑定提供了大量示例。
- 数据类型：`types.CutSpec` 和 `types.Data`。cut 机制目前还处于 alpha 阶段，
  它提供了一种便捷方式来裁剪 flow 数据。
- 路径：`types.Path`
