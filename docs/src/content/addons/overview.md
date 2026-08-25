---
title: "概览"
weight: 1
aliases:
  - /addons-overview/
---

# 插件 {#addons}

Mitmproxy 的插件机制是它异常强大的一部分。事实上，mitmproxy 自身的许多功能都定义在
[一整套内置插件](https://github.com/mitmproxy/mitmproxy/tree/main/mitmproxy/addons)中，
从[禁用缓存协商]({{< relref "/overview/features#anticache" >}})、
[粘性 Cookie]({{< relref "/overview/features#sticky-cookies" >}})
这类功能，一直到我们的引导安装 Web 应用，全都是这样实现的。

插件通过响应[事件]({{< relref event-hooks >}})与 mitmproxy 交互，从而挂接并改变 mitmproxy
的行为。它们通过[选项]({{< relref "/addons/options" >}})来配置，这些选项可以写在 mitmproxy
的配置文件里、由用户交互式修改，或者通过命令行传入。最后，它们还可以暴露
[命令]({{< relref "/addons/commands" >}})，让用户可以直接调用其动作，或者在交互式工具中把
它们绑定到按键上。

# 插件的结构 {#anatomy-of-an-addon}

{{< example src="examples/addons/anatomy.py" lang="py" >}}

上面是一个简单的插件，用来记录我们看到的 flow（更确切地说是 HTTP 请求）数量。每看到一条新的
flow，它就把计数加一并记录下来。输出可以在交互式工具的事件日志里找到，在 mitmdump 中则打印
到控制台。

把它加载到你选用的 mitmproxy 工具里跑一跑，确认它确实在做该做的事。我们在这些例子中用
mitmdump，但这个参数对所有工具都一样：

```bash
mitmdump -s ./anatomy.py
```

关于上面的代码，有几点值得注意：

- Mitmproxy 会读取全局列表 `addons` 的内容，并把其中找到的东西加载进插件机制。
- 插件就是普通对象——在这个例子里，我们的插件是 `Counter` 的一个实例。
- `request` 方法是一个*事件*的例子。插件只需为它想处理的每个事件实现一个方法即可。
  每个事件及其签名都记录在[API 文档]({{< relref "event-hooks" >}})中。

# 简写脚本语法 {#abbreviated-scripting-syntax}

有时候，我们想快速写个脚本，而不想麻烦地去创建一个类。插件机制提供了一种简写形式，
可以把整个模块当作一个插件对象。这样我们就可以把事件处理函数直接放在模块作用域里。
例如，下面是一个完整的脚本，它给每个请求添加一个头部：

{{< example src="examples/addons/anatomy2.py" lang="py" >}}

# 开发插件 {#developing-addons}

## 热重载 {#live-reloading}

用 `-s path/to/script.py` 加载的脚本会被监视改动。
每当文件的修改时间发生变化，mitmproxy 就会注销旧模块、重新导入文件并重新注册新插件——
而无需重启代理，也不会丢失其他插件的状态或正在传输中的 flow。这意味着你可以在编辑器里
修改插件，改动会在下一次保存时（大约一秒内）生效。

在导入时、在 `configure` 中或在 `running` 中抛出的错误会被记录到事件日志，并且插件的上一个
版本会保持在未注册状态。修好错误后再次保存文件即可重试。在事件处理器（`request`、
`response`、……）内部抛出的错误会被记录，但不会卸载插件。

## 测试插件 {#testing-addons}

由于插件就是普通的 Python 文件，对它们做单元测试最简单的方式就是：在测试里导入模块、
实例化插件，然后直接调用事件处理器。如果有更复杂的测试需求，可以参考
[`test/mitmproxy/addons`](https://github.com/mitmproxy/mitmproxy/tree/main/test/mitmproxy/addons)
（但请注意，内部测试辅助工具并不保证 API 稳定）。
