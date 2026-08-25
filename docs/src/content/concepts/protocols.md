---
title: "协议"
weight: 7
aliases:
  - /concepts-protocols/
---

# 协议 {#protocols}

mitmproxy 不仅支持 HTTP，也支持其他重要的 Web 协议。
本页列出各协议实现的细节和已知限制。
大多数协议都可以通过切换相应的[选项]({{< relref "/concepts/options" >}})来禁用。

## HTTP/1

mitmproxy 对 HTTP/1.0 和 HTTP/1.1 的支持基于我们自研的 HTTP 栈，后者构建在
[h11](https://github.com/python-hyper/h11) 之上，对 HTTP 语法错误特别健壮。
协议层面的违规常常会被代理有意转发或注入。

##### 已知限制 {#known-limitations}

- Trailer：mitmproxy 目前不支持 HTTP/1.x 的 trailer，但我们很乐意接受贡献。

## HTTP/2

mitmproxy 对 HTTP/2 的支持基于 [hyper-h2](https://github.com/python-hyper/hyper-h2)。
如果上游服务器不会说 HTTP/2，mitmproxy 会无缝地把消息转换成 HTTP/1。

##### 已知限制 {#known-limitations-1}

- *优先级信息*：mitmproxy 目前忽略 HTTP/2 PRIORITY 帧。这不影响传输的内容，
  但可能影响消息发送的顺序。
- *Push Promise*：mitmproxy 目前不声明支持 HTTP/2 Push Promise。
- *明文 HTTP/2*：mitmproxy 目前不支持未加密的 HTTP/2（h2c）。

## HTTP/3

mitmproxy 对 HTTP/3 的支持基于 [aioquic](https://github.com/aiortc/aioquic)。
mitmproxy 的 HTTP/3 功能在反向代理、本地抓包和 WireGuard 模式下可用。

##### 已知限制 {#known-limitations-2}

- *重放*：客户端重放目前是坏的。
- *支持的版本*：mitmproxy 目前只支持 QUIC 版本 1。版本 2（RFC 9369）尚不支持。
- *实现兼容性*：mitmproxy 的 HTTP/3 支持只针对 cURL 做过较充分的测试。
  其他实现很可能会暴露出 bug。

## WebSocket

mitmproxy 对 WebSocket 的支持基于 [wsproto](https://github.com/python-hyper/wsproto)
项目，包括对消息压缩的支持。

##### 已知限制 {#known-limitations-3}

- *重放*：客户端或服务端重放暂时都做不到。
- *Ping*：mitmproxy 会转发 PING 和 PONG 帧，但不会存储它们。载荷只会记录到事件日志。
- *未知扩展*：未知的 WebSocket 扩展会导致记录一条警告消息，但除此之外会被原样透传。
  这可能导致不符合规范的行为。

## DNS

mitmproxy 对 DNS 的支持基于自研的 DNS 实现。

##### 已知限制 {#known-limitations-4}

- *重放*：客户端或服务端重放暂时都做不到。
- 我们还没有开始做 DoT/DoH/DoQ（DNS-over-TLS/HTTPS/QUIC）方面的工作。欢迎贡献。

## 通用 TCP/TLS 代理 {#generic-tcptls-proxy}

Mitmproxy 也可以作为通用 TCP 代理使用。在这个模式下，mitmproxy 仍然会在连接开头检测是否
存在 TLS，并在必要时实施中间人攻击，但除此之外只是原样转发消息。

用户可以通过设置 [`tcp_hosts` 选项]({{< relref "/concepts/options" >}})显式启用通用 TCP 代理。

##### 已知限制 {#known-limitations-5}

- *重放*：客户端或服务端重放暂时都做不到。
- *机会式 TLS*：mitmproxy 无法检测明文协议何时升级为 TLS（STARTTLS）。


## 通用 UDP/DTLS 代理 {#generic-udpdtls-proxy}

Mitmproxy 也可以作为通用 UDP 代理使用。在这个模式下，mitmproxy 仍然会在连接开头检测是否
存在 DTLS，并在必要时实施中间人攻击，但除此之外只是原样转发消息。

用户可以通过设置 [`udp_hosts` 选项]({{< relref "/concepts/options" >}})显式启用通用 UDP 代理。

##### 已知限制 {#known-limitations-6}

- *重放*：客户端或服务端重放暂时都做不到。
