---
title: "忽略特定域名"
weight: 2
aliases:
  - /howto-ignoredomains/
---

# 忽略特定域名 {#ignoring-domains}

想把某些流量排除在 mitmproxy 的拦截机制之外，主要有两个原因：

- **证书固定：** 有些流量受
  [证书固定](https://security.stackexchange.com/questions/29988/what-is-certificate-pinning)
  保护，mitmproxy 的拦截会导致报错。例如，mitmproxy 处于活动状态时，Twitter 应用、
  Windows Update 或 Apple App Store 都会无法工作。
- **图个方便：** 你确实不关心流量中的某些部分，只想让它们消失。注意，在这种情况下
  mitmproxy 的 [view_filter]({{< relref "/concepts/options#view_filter" >}}) 选项往往是
  更好的选择，因为它不受下面列出的那些限制影响。

如果你想窥探（受 SSL 保护的）非 HTTP 连接，可以看看 **tcp_proxy** 功能。如果你是因为响应体
过大而想让流量绕过 mitmproxy 的处理，可以看看
[流式传输]({{< relref "/overview/features#streaming" >}})功能。

## ignore_hosts

`ignore_hosts` 选项允许你指定一个正则表达式，它会与连接的 `host:port` 字符串
（例如 "example.com:443"）进行匹配。匹配上的主机会被排除在拦截之外，原样透传。

|                    |                                                                    |
| ------------------ | ------------------------------------------------------------------ |
| 命令行别名         | `--ignore-hosts regex`                                             |
| mitmproxy 选项     | `ignore_hosts` |

## 限制 {#limitations}

有两个重要的怪异之处需要考虑：

- **在透明模式下，忽略模式匹配的是 IP 和 ClientHello 中的 SNI 主机名。** 虽然在设置了
  `ignore_hosts` 选项时我们通常会从 Host 头部推断主机名，但在 SSL 握手之前我们拿不到这个
  信息。不过，如果客户端使用了 SNI，我们就把 SNI 主机名当作忽略目标。
- **在常规代理和上游代理模式下，显式 HTTP 请求永远不会被忽略。**[^1] 忽略模式作用于
  CONNECT 请求，也就是发起 HTTPS 或明文 WebSocket 连接的那些请求。

## 教程 {#tutorial}

如果你只想忽略某一个特定域名，通常有一种万无一失的做法：

1. 运行 mitmproxy 或 mitmdump，观察事件日志中 `server connect` 消息后面的 `host:port`
   信息。mitmproxy 就是按这些来过滤的。
2. 取那个 `host:port` 字符串，用 ^ 和 $ 把它包起来，转义所有的点（. 变成 \\.），
    然后把它作为你的忽略模式：

```
>>> mitmdump
Proxy server listening at http://*:8080
127.0.0.1:57089: client connect
127.0.0.1:57089: server connect example.com:443 (93.184.216.34:443)
127.0.0.1:57089: GET https://example.com/ HTTP/2.0
     << HTTP/2.0 200 OK 1.23k
127.0.0.1:57089: client disconnect
127.0.0.1:57089: server disconnect example.com:443 (93.184.216.34:443)
^C
>>> mitmproxy --ignore-hosts '^example\.com:443$'
```

下面是一些其他的忽略模式示例：

```
# 排除来自 iOS App Store 的流量（这个正则比较宽松，但通常够用）：
--ignore-hosts apple.com:443
# 不会误匹配的“正确”版本：
--ignore-hosts '^(.+\.)?apple\.com:443$'

# 忽略 example.com，但不忽略它的子域名：
--ignore-hosts '^example.com:'

# 透明模式：
--ignore-hosts 17\.178\.96\.59:443
# IP 地址范围：
--ignore-hosts 17\.178\.\d+\.\d+:443
```

如果你只想抓取某些特定域名，可以使用 `--allow-hosts` 选项，它会让 mitmproxy 忽略所有其他
流量。

[^1]: 这源于显式 HTTP 代理的一个固有限制：一条连接可以被复用于多个目标域名——一个
      `GET http://example.com/` 请求之后，同一条连接上可能紧跟一个
      `GET http://evil.com/` 请求。如果我们在第一个请求之后就开始忽略这条连接，
      就会漏掉真正相关的第二个请求。
