---
title: "自定义选项"
weight: 3
aliases:
  - /addons-options/
---

# 选项 {#options}

mitmproxy 的核心是一个全局选项存储，其中保存着决定 mitmproxy 及其插件行为的设置。选项可以
从配置文件读取、在命令行上设置，也可以由用户在运行中交互式修改。

所有选项都用一组受支持的类型之一做了注解。Mitmproxy 知道如何序列化和反序列化这些类型，
并且有标准的方式在交互式程序中呈现带类型的值以供编辑。试图用错误的类型设置值会导致报错。
这意味着插件选项只要声明了类型，就能在 mitmproxy 的整条工具链中获得完整支持。

## 简单示例 {#simple-example}

{{< example src="examples/addons/options-simple.py" lang="py" >}}

`load` 事件会收到一个 `mitmproxy.addonmanager.Loader` 实例，它让插件可以声明选项和命令。
在这个例子里，插件添加了一个类型为 `bool` 的 `addheader` 选项。我们在 mitmproxy 控制台里
运行这个脚本试试：

```bash
> mitmproxy -s ./examples/addons/options-simple.py
```

现在你可以像这样用 CURL 通过代理发一个请求：

```bash
> env http_proxy=http://localhost:8080 curl -I http://google.com
```

如果你立刻运行这个请求，会发现并没有添加 count 头部。这是因为该选项的默认值是 `false`。
按 `O` 进入选项编辑器，找到 `addheader` 选项。你会注意到 mitmproxy 知道这是一个布尔值，
并允许你在 true 和 false 之间切换。把值设为 `true`，你应该会看到类似这样的结果：

```bash
> env http_proxy=http://localhost:8080 curl -I http://google.com
HTTP/1.1 301 Moved Permanently
Location: http://www.google.com/
Content-Length: 219
count: 1
```

加载这个插件后，`addheader` 设置就可以出现在持久化的
[YAML 配置文件]({{< relref "/concepts/options" >}})中了。你也可以对任意工具使用 `--set`
参数，直接在命令行上覆盖该值：

```bash
mitmproxy -s ./examples/addons/options-simple.py --set addheader=true
```

## 处理配置更新 {#handling-configuration-updates}

有时候，仅仅在某个事件中读取选项的值还不够。我们希望在用户修改选项时立即做出反应。
这就是 `configure` 事件的用途——它被触发时，会收到一组发生变化的选项。插件可以检查某个选项
是否在这组里，然后从上下文的 options 对象读取其值。

这个功能的一个常见用途是校验选项是否合法，如果不合法就给用户反馈。如果在 configure 期间
抛出了 `exceptions.OptionsError` 异常，本次更新中的所有改动都会被自动回滚，并向用户显示
一条错误。我们来看个例子。

{{< example src="examples/addons/options-configure.py" lang="py" >}}

这里有几点需要注意。首先，我们添加的选项使用了 `typing.Optional`。这告诉 mitmproxy
`None` 对该选项是合法值——也就是说它可以处于未设置状态。其次，`configure` 方法第一次是用
我们的默认值（`None`）调用的，之后如果选项被修改，会再用新值调用一次。如果我们试着用一个
不正确的值加载脚本，现在就会看到错误：

```
> mitmdump -s ./examples/addons/options-configure.py --set addheader=1000
Loading script: ./examples/addons/options-configure.py
/Users/cortesi/mitmproxy/mitmproxy/venv/bin/mitmdump: addheader must be <= 100
```

## 支持的类型 {#supported-types}

选项支持下列类型。

- 基本类型——`str`、`int`、`float`、`bool`。
- 可选值，用 `typing.Optional` 注解。
- 值的序列，用 `collections.abc.Sequence` 注解。
