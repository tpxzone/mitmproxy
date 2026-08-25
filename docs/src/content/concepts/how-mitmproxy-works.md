---
title: "mitmproxy 的工作原理"
weight: 1
aliases:
  - /concepts-howmitmproxyworks/
---

# mitmproxy 的工作原理 {#how-mitmproxy-works}

Mitmproxy 是一个极其灵活的工具。准确了解代理过程是如何运作的，有助于你创造性地部署它，
也有助于你考虑到它的基本假设以及如何绕开这些限制。本文详细解释 mitmproxy 的代理机制，
从最简单的未加密显式代理开始，一直讲到最复杂的场景——在存在
[服务器名称指示（SNI）](https://en.wikipedia.org/wiki/Server_Name_Indication)
的情况下，透明代理受 TLS 保护的流量[^1]。

## 显式 HTTP {#explicit-http}

把客户端配置为使用 mitmproxy 作为显式代理，是拦截流量最简单也最可靠的方式。代理协议在
[HTTP RFC](https://tools.ietf.org/html/rfc7230) 中已有明文规定，因此客户端和服务器双方的
行为都有明确定义，通常也很可靠。在与 mitmproxy 最简单的交互中，客户端直接连接到代理，
并发出这样一个请求：

```http
GET http://example.com/index.html HTTP/1.1
```

这是一个代理 GET 请求——普通 HTTP GET 请求的扩展形式，其中包含了 scheme 和主机信息，
也就包含了 mitmproxy 继续处理所需的全部信息。

{{< figure src="/schematics/how-mitmproxy-works-explicit.png" title="显式代理" >}}

1. 客户端连接到代理并发出请求。
2. Mitmproxy 连接到上游服务器，直接把请求转发过去。

## 显式 HTTPS {#explicit-https}

显式代理的 HTTPS 连接，其过程则相当不同。客户端连接到代理，并发出这样一个请求：

```http
CONNECT example.com:443 HTTP/1.1
```

传统代理既不能查看也不能操纵 TLS 加密的数据流，因此 CONNECT 请求只是要求代理在客户端和
服务器之间打开一条管道。这里的代理只是一个中转者——它在两个方向上盲目地转发数据，对内容
一无所知。TLS 连接的协商就发生在这条管道之上，随后的请求和响应流对代理而言完全不可见。

### mitmproxy 里的 MITM {#the-mitm-in-mitmproxy}

这正是 mitmproxy 的根本手法发挥作用的地方。名字里的 MITM 代表 Man-In-The-Middle
（中间人），指的就是我们用来拦截并干预这些理论上不透明的数据流的过程。基本思路是：
对客户端假装自己是服务器，对服务器假装自己是客户端，而我们坐在中间解码两侧的流量。
麻烦之处在于，[证书颁发机构](https://en.wikipedia.org/wiki/Certificate_authority)（CA）
体系恰恰就是为了防止这种攻击而设计的：它让一个受信任的第三方对服务器证书进行密码学签名，
以证明证书是合法的。如果签名不匹配，或者来自不受信任的一方，一个安全的客户端就会直接
断开连接、拒绝继续。尽管当今的 CA 体系存在诸多不足，但这通常足以让为了分析而中间人化
TLS 连接的尝试彻底失败。我们对这一难题的答案是：自己成为一个受信任的证书颁发机构。
Mitmproxy 内置了完整的 CA 实现，可以实时生成拦截证书。为了让客户端信任这些证书，
我们需要[手动把 mitmproxy 注册为设备上受信任的 CA]({{< relref "/concepts/certificates" >}})。

### 复杂点 1：远端主机名是什么？ {#complication-1-whats-the-remote-hostname}

要推进这个方案，我们需要知道拦截证书中应该使用的域名——客户端会校验证书是否签发给它正在
连接的那个域名，若不是就会中止。乍看之下，上面的 CONNECT 请求似乎已经给了我们所需的一切
信息——在这个例子里，这两个值都是 “example.com”。但如果客户端是这样发起连接的呢：

```http
CONNECT 10.1.1.1:443 HTTP/1.1
```

使用 IP 地址完全合法，因为它已经给出了建立管道所需的足够信息，即便它并没有透露远端主机名。

Mitmproxy 有一个巧妙的机制来化解这一点——[上游证书嗅探]({{< relref
"/concepts/certificates#upstream-certificate-sniffing" >}})。一看到 CONNECT 请求，
我们就暂停与客户端的会话，同时发起一个到服务器的连接。我们与服务器完成 TLS 握手，
并检查它所使用的证书。接着，我们用上游证书中的 Common Name 来为客户端生成伪造证书。
瞧——即便主机名从未被明确指定，我们也拿到了要呈现给客户端的正确主机名。

### 复杂点 2：主题备用名称 {#complication-2-subject-alternative-name}

接着是下一个复杂点。有时候，证书的 Common Name 实际上并不是客户端正在连接的那个主机名。
这是因为证书中有一个可选的
[主题备用名称](https://en.wikipedia.org/wiki/SubjectAltName)（SAN）字段，
允许指定任意数量的备用域名。如果期望的域名匹配其中任何一个，客户端就会继续，即使该域名
与证书的 CN 并不匹配。这里的解法很简单：我们在从上游证书提取 CN 的同时，也提取 SAN，
并把它们加到生成的伪造证书里。

### 复杂点 3：服务器名称指示 {#complication-3-server-name-indication}

原始 TLS 的一大局限是每张证书都需要独立的 IP 地址。这意味着你无法做虚拟主机，
让多个拥有各自证书的域名共用同一个 IP 地址。在 IPv4 地址池快速枯竭的今天这是个问题，
而我们的解法就是 TLS 协议的
[服务器名称指示](https://en.wikipedia.org/wiki/Server_Name_Indication)（SNI）扩展。
它让客户端在 TLS 握手一开始就指定远端服务器名，服务器随后便可以挑选正确的证书来完成握手。

SNI 破坏了我们的上游证书嗅探过程，因为当我们不使用 SNI 去连接时，拿到的是一张默认证书，
它可能与客户端所期望的证书毫无关系。解法是在客户端连接流程上再加一层巧妙的处理：客户端
连上来之后，我们让 TLS 握手继续，直到 SNI 值被传给我们之**后**才停下。此时我们就可以
暂停会话，用正确的 SNI 值发起上游连接，从而拿到正确的上游证书，再从中提取出期望的 CN 和 SAN。

### 把这些拼起来 {#putting-it-all-together}

让我们把上面这些拼成完整的显式代理 HTTPS 流程。

{{< figure src="/schematics/how-mitmproxy-works-explicit-https.png" title="显式 HTTPS" >}}

1. 客户端连接到 mitmproxy，并发出一个 HTTP CONNECT 请求。
2. Mitmproxy 回复 `200 Connection Established`，仿佛它已经建立好了 CONNECT 管道。
3. 客户端以为自己在和远端服务器通信，于是发起 TLS 连接。它用 SNI 指明自己要连接的主机名。
4. Mitmproxy 连接到服务器，使用客户端指明的 SNI 主机名建立 TLS 连接。
5. 服务器返回匹配的证书，其中包含生成拦截证书所需的 CN 和 SAN 值。
6. Mitmproxy 生成拦截证书，并继续在第 3 步中被暂停的客户端 TLS 握手。
7. 客户端通过已建立的 TLS 连接发送请求。
8. Mitmproxy 通过第 4 步发起的 TLS 连接把请求转发给服务器。

## 透明 HTTP {#transparent-http}

使用透明代理时，连接会在网络层被重定向到代理，无需对客户端做任何配置。这使得透明代理
非常适合那些你无法改变客户端行为的场景——不感知代理的 Android 应用就是一个常见例子。

要做到这一点，我们需要引入两个额外的组件。第一个是重定向机制，它把本应发往互联网上某台
服务器的 TCP 连接透明地改道到一个正在监听的代理服务器。这通常表现为与代理服务器同主机的
一个防火墙——Linux 上的 [iptables](http://www.netfilter.org/) 或 OSX 上的
[pf](https://en.wikipedia.org/wiki/PF_\(firewall\))。客户端发起连接之后，它会发出一个
普通的 HTTP 请求，大致长这样：

```http
GET /index.html HTTP/1.1
```

注意这个请求与显式代理的版本不同，它省略了 scheme 和主机名。那么我们怎么知道该把请求转发
给哪个上游主机呢？执行了重定向的路由机制会帮我们记录原始目的地。每种路由机制暴露这一数据
的方式各不相同，于是这就引出了透明代理正常工作所需的第二个组件：一个知道如何从路由器取回
原始目的地址的主机模块。在 mitmproxy 中，它表现为一组内置
[模块](https://github.com/mitmproxy/mitmproxy/tree/main/mitmproxy/platform)，
它们知道如何与各平台的重定向机制打交道。一旦拿到这一信息，整个过程就相当直接了。

{{< figure src="/schematics/how-mitmproxy-works-transparent.png" title="透明代理" >}}

1. 客户端向服务器发起连接。
2. 路由器把连接重定向到 mitmproxy，后者通常监听在同一主机的某个本地端口上。
    Mitmproxy 随后查询路由机制，确定原始目的地是什么。
3. 接着，我们只需读取客户端的请求……
4. ……并把它转发给上游。

## 透明 HTTPS {#transparent-https}

第一步是判断是否应该把一个进来的连接当作 HTTPS 来处理。做这件事的机制很简单——我们用路由
机制查出原始目的端口。所有进来的连接都会经过不同的层，这些层可以确定实际要使用的协议。
自动 TLS 检测通过在每个连接开头查找 *ClientHello* 消息，对 SSLv3、TLS 1.0、TLS 1.1 和
TLS 1.2 都有效。这与所使用的 TCP 端口无关。

从这里开始，整个过程就是我们前面描述的透明代理 HTTP 与显式代理 HTTPS 两种方法的结合。
我们用路由机制确定上游服务器地址，然后按显式 HTTPS 连接的方式确定 CN 和 SAN，并处理 SNI。

{{< figure src="/schematics/how-mitmproxy-works-transparent-https.png" title="透明 HTTPS" >}}

1. 客户端向服务器发起连接。
2. 路由器把连接重定向到 mitmproxy，后者通常监听在同一主机的某个本地端口上。
    Mitmproxy 随后查询路由机制，确定原始目的地是什么。
3. 客户端以为自己在和远端服务器通信，于是发起 TLS 连接。它用 SNI 指明自己要连接的主机名。
4. Mitmproxy 连接到服务器，使用客户端指明的 SNI 主机名建立 TLS 连接。
5. 服务器返回匹配的证书，其中包含生成拦截证书所需的 CN 和 SAN 值。
6. Mitmproxy 生成拦截证书，并继续在第 3 步中被暂停的客户端 TLS 握手。
7. 客户端通过已建立的 TLS 连接发送请求。
8. Mitmproxy 通过第 4 步发起的 TLS 连接把请求转发给服务器。

### 脚注 {#footnotes}

[^1]: 除另有说明外，文中提到的 “TLS” 在泛指意义上同时涵盖 SSL（已过时且不安全）
    和 TLS（1.0 及以上）。
