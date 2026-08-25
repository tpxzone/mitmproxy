---
title: "API 变更日志"
weight: 9
aliases:
  - /addons-api-changelog/
---

# API 变更日志 {#api-changelog}

我们尽量避免破坏性变更，但本页仍会列出 mitmproxy 插件 API 中的破坏性改动。

## mitmproxy 12

内容视图（Contentviews）API 大幅简化，详情请参见新的[内容视图文档]。

[内容视图文档]: {{< relref "/addons/contentviews" >}}

`mitmproxy.dns.Message` 已重命名为 `mitmproxy.dns.DNSMessage`。

## mitmproxy 9.1

`mitmproxy.connection.Client` 和 `mitmproxy.connection.Server` 现在只接受关键字参数。

## mitmproxy 9.0

#### 日志 {#logging}

我们弃用了 mitmproxy 自研的日志系统，转而使用 Python 内置的 `logging` 模块。
这意味着插件现在应该使用标准的 logging 功能，而不是 `mitmproxy.ctx.log`：

```python
# 已弃用：
from mitmproxy import ctx

ctx.log.info("hello world")

# 新写法：
import logging

logging.info("hello world")
```


相应地，`add_log` 事件也被弃用。依赖日志条目的开发者应改为注册自己的 `logging.Handler`。
可以在 `EventStore` 插件中找到相关示例。

## mitmproxy 7.0

#### 连接事件 {#connection-events}

作为新代理内核的一部分，我们修订了 mitmproxy 中与连接相关的事件钩子。`.client_conn` 和
`.server_conn` 对象在各方面都有重大的 API 变更。详情请参见新的
[事件钩子文档]({{< relref "/addons/event-hooks#ConnectionEvents" >}})。

| 属性            | 客户端（v6） | 服务端（v6）      | mitmproxy v7 |
|-----------------|--------------|-------------------|--------------|
| 远端 IP:端口    | `.address`   | `.ip_address`     | `.peername`  |
| 本地 IP:端口    | ❌           | `.source_address` | `.sockname`  |
| 远端域名        | 不适用       | `.address`        | `.address`   |


由于现在传入的对象已经不同，我们也借此机会引入了更一致的事件命名：

| mitmproxy 6        | mitmproxy 7           |
| ------------------ | --------------------- |
| `clientconnect`    | `client_connected`    |
| `clientdisconnect` | `client_disconnected` |
| ❌                 | `server_connect`      |
| `serverconnect`    | `server_connected`    |
| `serverdisconnect` | `server_disconnected` |

#### 日志 {#logging-1}

`log` 事件已重命名为 `add_log`。这修掉了一个反复出现的错误来源：用户导入了名为 “log” 的
模块，结果被无意中当成了事件处理器。

#### 内容视图 {#contentviews}

内容视图现在实现 `render_priority` 而不是 `should_render`。这使得进一步特化成为可能，
例如现在可以编写只美化特定 JSON 响应的内容视图。
详情请参见 [contentview.py]({{< relref "/addons/examples#contentview" >}}) 示例。

#### WebSocket Flow {#websocket-flows}

mitmproxy 6 有一个自定义的 WebSocketFlow 类，它与相关的 HTTPFlow 之间存在
[难看的相互依赖](https://github.com/mitmproxy/mitmproxy/issues/4425)。长话短说，
WebSocketFlow 不再存在，取而代之的是 HTTPFlow 有了一个清爽的
[`.websocket` 属性]({{< relref "api/mitmproxy.http.md#HTTPFlow.websocket" >}})。
现在所有 WebSocket flow 传入的都是设置了该属性的原始 `HTTPFlow`。一如既往，
已有的 dump 文件在加载时会自动转换。

#### 证书 {#certificates}

mitmproxy 现在使用 `cryptography` 而不是 `pyOpenSSL` 来生成证书。因此，
`mitmproxy.certs` 的 API 发生了变化。

#### HTTP 头部 {#http-headers}

为保持一致，`mitmproxy.net.http.Headers` 改为 `mitmproxy.http.Headers`。
