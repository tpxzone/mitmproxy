---
title: "代理模式"
weight: 2
aliases:
  - /concepts-modes/
---

# 代理模式 {#proxy-modes}

mitmproxy 支持多种代理模式来抓取流量。
任意一种模式都可以与任意一个 mitmproxy 工具（mitmproxy、mitmweb 或 mitmdump）配合使用。


### 推荐模式 {#recommended}

- [常规（Regular）](#regular-proxy)：默认模式。把你的客户端配置为使用 HTTP(S) 代理。
- [本地抓包（Local Capture）](#local-capture)：抓取同一台设备上的应用。
- [WireGuard](#wireguard)：抓取外部设备或单个 Android 应用。
- [反向（Reverse）](#reverse-proxy)：把 mitmproxy 放在服务器前面。

### 进阶模式 {#advanced-modes}

- [透明（Transparent）](#transparent-proxy)：通过自定义网络路由抓取流量。
- [TUN 接口](#tun-interface)：创建一个虚拟网络设备来抓取流量。
- [上游（Upstream）](#upstream-proxy)：串联两个 HTTP(S) 代理。
- [SOCKS](#socks-proxy)：运行一个 SOCKS5 代理服务器。
- [DNS](#dns-server)：运行一个可脚本化的 DNS 服务器。


## 常规代理 {#regular-proxy}

mitmproxy 的常规模式是最简单、也是最稳健的搭建方式。
如果你的目标可以配置为使用 HTTP 代理，我们建议你从这个模式开始。

1. 启动 `mitmproxy`、`mitmdump` 或 `mitmweb`。不需要传任何参数。
2. 通过显式设置 HTTP 代理，把你的客户端配置为使用 mitmproxy。
    默认情况下 mitmproxy 监听 8080 端口。
3. 快速检查：此时你应该已经能通过代理访问未加密的 HTTP 站点了。
4. 打开魔法域名 **mitm.it**，为你的设备安装证书。

### 排障 {#troubleshooting}

1. 如果你在 mitmproxy 中看不到任何流量，请打开 mitmproxy 的事件日志。
   你应该能在其中看到 `client connect` 消息。
   如果看不到 `client connect` 消息，说明你的客户端根本没有到达代理：
      - 可能是 IP 地址或端口配置错了。
      - 也可能是你的无线网络启用了<em>客户端隔离</em>，它会阻止客户端之间互相通信。
2. 有些应用会绕过操作系统的 HTTP 代理设置——Android 应用就是常见的例子。这种情况下，
   你需要使用 mitmproxy 的 [WireGuard](#wireguard)、[本地抓包](#local-capture)
   或[透明](#transparent-proxy)模式。

#### 网络拓扑 {#network-topology}

如果你在代理一台外部设备，你的网络大概长这样：

{{< figure src="/schematics/proxy-modes-regular.png" >}}

方括号表示源 IP 地址和目的 IP 地址。你的客户端显式地连接 mitmproxy，
mitmproxy 再显式地连接目标服务器。


## 本地抓包 {#local-capture}

本地抓包模式会透明地抓取运行在同一台设备上的应用的流量。
你可以抓取当前设备上的全部流量，也可以只抓取某个特定进程名或进程 ID（PID）：

```shell
mitmproxy --mode local       # 拦截本机上的所有流量。
mitmproxy --mode local:curl  # 只拦截 cURL。
mitmproxy --mode local:42    # 只拦截 PID 42。
```

本地抓包是用底层操作系统 API 实现的，因此拦截是透明的，目标应用并不知道自己被代理了。

如果你对实现细节感兴趣，可以看看
[发布博文](https://mitmproxy.org/tags/local-capture/)。本地抓包在 Windows、Linux
和 macOS 上均可用。

#### 拦截规格 {#intercept-specs}

在目标前面加一个感叹号可以取反：

```shell
mitmproxy --mode local:!curl  # 拦截本机上除 cURL 之外的所有流量。
```

也可以提供一个以逗号分隔的列表：

```shell
mitmproxy --mode local:curl,wget    # 只拦截 cURL 和 wget。
mitmproxy --mode local:!curl,!wget  # 拦截除 cURL 和 wget 之外的所有流量。
```

#### Linux 上本地抓包的限制 {#local-capture-limitations-on-linux}

- **仅出向：** mitmproxy 只会抓取出向连接。
  对于入向连接，我们推荐使用反向代理模式。
- **root 权限：** 为了加载 BPF 程序，mitmproxy 需要用 `sudo` 启动一个特权子进程。
  对 Web 界面来说，这意味着 mitmweb 需要在命令行上直接带 `--mode local` 启动，
  才能弹出 sudo 密码提示。
- **内核兼容性：** 我们的 eBPF 探针需要相对较新的内核。
  我们官方支持 Linux 6.8 及以上，对应 Ubuntu 22.04。
- **拦截规格：** 程序名只匹配前 16 个字符（受内核 [TASK_COMM_LEN] 限制）。
- **容器：** 除非容器使用主机网络，否则抓取容器流量会失败。
  例如，容器可以用 `docker/podman run --network host` 启动。
- **Windows Subsystem for Linux（WSL 1/2）：** 不支持 WSL，因为其默认禁用 eBPF。

[TASK_COMM_LEN]: https://github.com/torvalds/linux/blob/fbfd64d25c7af3b8695201ebc85efe90be28c5a3/include/linux/sched.h#L306

#### macOS 上本地抓包的限制 {#local-capture-limitations-on-macos}

- **仅出向：** mitmproxy 只会抓取出向连接。
  对于入向连接，我们推荐使用反向代理模式。

## WireGuard

在 WireGuard 模式下，mitmproxy 会启动一个 WireGuard VPN 服务器。设备可以用标准的
WireGuard 客户端应用连上来，mitmproxy 会透明地拦截它们的流量。

1. 启动 `mitmweb --mode wireguard`。
2. 在目标设备上安装 WireGuard 客户端。
3. 导入 mitmproxy 提供的 WireGuard 客户端配置。

不需要额外的路由配置。WireGuard 服务器完全运行在用户态，因此该模式下不需要管理员权限。

### 配置 {#configuration}

#### WireGuard 服务器 {#wireguard-server}

默认情况下，WireGuard 服务器会监听 `51820/udp`，这是 WireGuard 服务器的默认端口。
可以通过设置 `listen_port` 选项或显式指定端口（`--mode wireguard@51821`）来修改。

WireGuard 连接的加密密钥保存在 `~/.mitmproxy/wireguard.conf`。可以用
`--mode wireguard:path` 指定自定义路径。如果指定的文件还不存在，会自动生成新密钥。
例如，要同时连接两个客户端，你可以运行
`mitmdump --mode wireguard:wg-keys-1.conf --mode wireguard:wg-keys-2.conf@51821`。

#### WireGuard 客户端 {#wireguard-clients}

可以把经由 WireGuard 隧道发送的流量限定在特定的 IP 地址范围内。这时，可以把 WireGuard
客户端配置中的 `AllowedIPs` 设置从 `0.0.0.0/0`（即“把*所有* IPv4 流量都走 WireGuard
隧道”）改成你想要的 IP 地址范围（该设置支持多个以逗号分隔的值）。

对于更复杂的网络布局，可能还需要覆盖自动检测出的 `Endpoint` IP 地址（即运行 mitmproxy
及其 WireGuard 服务器的那台主机的地址）。

### 限制 {#limitations}

#### 透明代理 mitmproxy 主机自身的流量 {#transparently-proxying-mitmproxy-host-traffic}

在当前实现下，无法代理 mitmproxy 自身所在主机的全部流量，因为那会导致出向的 WireGuard
报文本身也被送进 WireGuard 隧道。

#### 对 IPv6 流量的支持有限 {#limited-support-for-ipv6-traffic}

mitmproxy 内置的 WireGuard 服务器支持接收来自客户端设备的 IPv6 报文，但对代理 IPv6
报文本身的支持仍然有限。因此，生成的 WireGuard 客户端配置中的 `AllowedIPs` 设置暂时不会
列出任何 IPv6 地址。要启用这一尚不完整的 IPv6 流量支持，可以把 `::/0`（即“把*所有*
IPv6 流量都走 WireGuard 隧道”）或其他 IPv6 地址范围加入允许的 IP 地址列表。


## 反向代理 {#reverse-proxy}

```shell
mitmdump --mode reverse:https://example.com
```

在反向代理模式下，mitmproxy 表现得像一台普通服务器。
客户端的请求会被转发给一台预先配置好的目标服务器，响应再转发回客户端：

{{< figure src="/schematics/proxy-modes-reverse.png" >}}

### 监听端口 {#listen-port}

除 DNS 之外，反向代理服务器默认监听 8080 端口（DNS 用 53）。
要监听其他端口，在模式后面追加 `@端口号`。你也可以重复传入 `--mode`，在不同端口上运行
多个反向代理服务器。例如，下面的命令会在 80 和 443 端口各运行一个指向 example.com 的
反向代理服务器：

```text
mitmdump --mode reverse:https://example.com@80 --mode reverse:https://example.com@443
```

### 协议规格 {#protocol-specification}

上面的例子聚焦于 HTTP 反向代理，但 mitmproxy 也可以反向代理其他协议。
要调整协议，只需调整代理规格中的 scheme。例如 `--mode reverse:tcp://example.com:80`
会建立一个裸 TCP 代理。

| Scheme   | 客户端 ↔ mitmproxy                | mitmproxy ↔ 服务器      |
|----------|-----------------------------------|-------------------------|
| http://  | HTTP 或 HTTPS（自动检测）         | HTTP                    |
| https:// | HTTP 或 HTTPS（自动检测）         | HTTPS                   |
| dns://   | DNS                               | DNS                     |
| http3:// | HTTP/3                            | HTTP/3                  |
| quic://  | 裸 QUIC                           | 裸 QUIC                 |
| tcp://   | 裸 TCP 或 TCP-over-TLS（自动检测）| 裸 TCP                  |
| tls://   | 裸 TCP 或 TCP-over-TLS（自动检测）| 裸 TCP-over-TLS         |
| udp://   | 裸 UDP 或 UDP-over-DTLS（自动检测）| 裸 UDP                 |
| dtls://  | 裸 UDP 或 UDP-over-DTLS（自动检测）| 裸 UDP-over-DTLS       |


### 反向代理示例 {#reverse-proxy-examples}

- 假设你有一个内部 API 跑在 <http://example.local/>。你现在可以在
  <http://debug.example.local/> 上以反向代理模式搭起 mitmproxy，并动态地把客户端指向
  这个新的 API 端点：客户端拿到的是同样的数据，而你拿到的是调试信息。同理，你也可以把
  真实服务器挪到另一个 IP/端口，然后在原来的位置搭起 mitmproxy，用来调试和/或重定向
  所有会话。
- 假设你是一名 Web 开发者，正在开发 <http://example.com/>（开发版本跑在
  <http://localhost:8000/>）。你可以修改 hosts 文件，让 example.com 指向 127.0.0.1，
  然后在 80 端口以反向代理模式运行 mitmproxy。这样你就可以在 example.com 域名上测试你的
  应用，并让所有请求都被 mitmproxy 记录下来。
- 假设你有个玩具项目需要支持 TLS。只要在 443 端口把 mitmproxy 搭成反向代理就搞定了
  （`mitmdump -p 443 --mode reverse:http://localhost:80/`）。Mitmproxy 会自动检测 TLS
  流量并动态拦截它。针对这个具体任务当然有更好的工具，但 mitmproxy 是一种非常快速简单的
  方式，能立刻搭起一个会说 TLS 的服务器。
- 想知道 (D)TLS 之上（非 HTTP）都发生了什么？借助 mitmproxy 的裸流量支持你可以做到。
  用 `--mode reverse:tls://example.com:1234` 启动一个 TCP 实例，它会用 TLS 连接
  `example.com:1234`；用 `--mode reverse:dtls://example.com:1234` 则分别改用 UDP 和 DTLS。
  进来的客户端连接既可以自己使用 (D)TLS，也可以是裸 TCP/UDP。
  如果你只想对部分主机检查裸流量、对其他主机走 HTTP，可以看看
  [tcp_hosts]({{< relref "/concepts/options" >}}#tcp_hosts) 和
  [udp_hosts]({{< relref "/concepts/options" >}}#udp_hosts) 选项。
- 假设你想抓取发往 Google 公共 DNS 服务器的 DNS 流量？那就用
  `--mode reverse:dns://8.8.8.8` 启动一个反向实例。如果你想在本地解析查询（即使用
  操作系统提供并配置的解析能力），请改用 [DNS 服务器](#dns-server)模式。

### Host 头部 {#host-header}

在反向代理模式下，mitmproxy 会自动改写 Host 头部以匹配上游服务器。这让 mitmproxy 能够
轻松连接公网上已有的端点（例如 `mitmproxy --mode reverse:https://example.com`）。
你可以用 `keep_host_header` 选项禁用这一行为。

不过要记住，返回文档中的绝对 URL 以及 HTTP 重定向**不会**被 mitmproxy 改写。这意味着
如果你在返回的网页中点击了指向 “<http://example.com>” 的链接，你会被直接带到那个 URL，
从而绕过 mitmproxy。

一种可能的应对方式是修改操作系统的 hosts 文件，让 “example.com” 解析到你代理的 IP，
然后直接访问 example.com 来访问代理。要确保你的代理仍然能解析出原始 IP，或者在 mitmproxy
中指定一个 IP。

{{% note %}}

### 注意：交互式使用 {#caveat-interactive-use}

反向代理模式通常不足以在另一个 URL 上复制出一个交互式网站。返回给客户端的 HTML 保持
不变——一旦用户点击了非相对 URL（或下载了非相对的图片资源），流量就不再经过 mitmproxy 了。
{{% /note %}}


## 透明代理 {#transparent-proxy}

{{% note %}}
可以考虑使用 [WireGuard](#wireguard) 和[本地抓包](#local-capture)模式来代替透明模式。
它们搭建起来更简单，而且还支持基于 UDP 的协议（透明模式目前不支持）。
{{% /note %}}

*可用平台：Linux、macOS*

在透明模式下，流量在网络层被导入代理，无需任何客户端配置。这使得透明代理非常适合那些
你无法改变客户端行为的场景：

```shell
mitmdump --mode transparent
```

在下图中，一台运行 mitmproxy 的机器被插入到了路由器和互联网之间：

{{< figure src="/schematics/proxy-modes-transparent-1.png" >}}

方括号表示源 IP 地址和目的 IP 地址。圆括号标注的是*以太网/数据链路*层的下一跳。
这个区分很重要：报文到达 mitmproxy 所在机器时，其目的地址必须仍然是目标服务器。
这意味着在流量到达 mitmproxy 之前不应做网络地址转换（NAT），否则目标信息会被抹掉，
mitmproxy 就无法确定真正的目的地了。

{{< figure src="/schematics/proxy-modes-transparent-wrong.png" >}}

### 常见配置 {#common-configurations}

为透明代理配置网络的方式有很多。我们来看两种常见场景：

1. 把客户端配置为使用自定义网关/路由器/“下一跳”
2. 在路由器上实现自定义路由

大多数情况下，由于易于使用，推荐第一种方案。

#### （a）自定义网关 {#a-custom-gateway}

要让流量在保留目的 IP 的前提下到达 mitmproxy 所在机器，一种简单的做法是：直接把客户端
的默认网关配置为 mitmproxy 所在的机器。

{{< figure src="/schematics/proxy-modes-transparent-2.png" >}}

在这个场景下，我们要：

1. 把代理机器配置为透明模式。相关说明可以在[透明代理]({{< relref "/howto/transparent"
    >}})一节中找到。
2. 把客户端的默认网关配置为代理机器的 IP。
3. 快速检查：此时你应该已经能通过代理访问未加密的 HTTP 站点了。
4. 打开魔法域名 **mitm.it**，为你的设备安装证书。

在客户端上设置自定义网关这件事可以通过 DHCP 下发设置来自动化。这样你就能搭起一个拦截
网络，其中所有客户端都被自动代理，可以省下不少时间和精力。

{{% note %}}

### 透明模式排障 {#troubleshooting-transparent-mode}

透明模式配置错误是常见的问题来源。如果对你不起作用，可以试试下面这些：

- 打开 mitmproxy 的事件日志——你看到 clientconnect 消息了吗？如果没有，说明报文没有到达
    代理。一个常见原因是出现了 ICMP 重定向，也就是你的机器告诉客户端“直接联系你的路由器
    有更快的上网路径”（关于如何禁用它，请看[透明代理]({{< relref "/howto/transparent"
    >}})一节）。如果拿不准，[Wireshark](https://wireshark.org/) 可以帮你看清到底有没有
    东西到达你的机器。
- 确认你没有在客户端上显式配置 HTTP 代理。透明模式下不需要这么做。
- 重新检查[透明代理]({{< relref "/howto/transparent"
    >}})一节中的说明。有没有漏掉什么？

如果你遇到了其他应该列在这里的坑，请告诉我们！
{{% /note %}}

#### （b）自定义路由 {#b-custom-routing}

在某些情况下，你可能需要更细粒度地控制哪些流量进入 mitmproxy 实例、哪些不进入。
比如说，你可能只想把发往某些主机的流量导入透明代理。实现方式非常多，很大程度上取决于
你使用的路由器或包过滤器。大多数情况下，配置会长这样：

{{< figure src="/schematics/proxy-modes-transparent-3.png" >}}

## TUN 接口 {#tun-interface}

*可用平台：Linux*

```shell
sudo mitmdump --mode tun
```

在 TUN 模式下，mitmproxy 会在系统上创建一个虚拟网络接口。所有路由到该接口的流量都会被
mitmproxy 拦截。例如，`curl --interface tun0 http://example.com/` 就会被透明拦截。
对大多数应用来说，你需要手动配置本地路由表。

你可以选择指定一个固定的接口名：

```shell
sudo mitmdump --mode tun:mitm-tun
```

该模式需要 root 权限（或在 Python 解释器上具备 `CAP_NET_ADMIN`）才能创建 tun 接口。

#### 在容器中使用 {#usage-with-containers}

Mitmproxy 的 [docker-entrypoint.sh] 默认会在启动时丢弃所有权限。
要让 TUN 模式在 Linux 容器中工作，你可以这样做：

```shell
docker run --privileged --network host mitmproxy/mitmproxy bash -c "mitmdump --mode tun"
```

[docker-entrypoint.sh]: https://github.com/mitmproxy/mitmproxy/blob/main/release/docker/docker-entrypoint.sh

## 上游代理 {#upstream-proxy}

```shell
mitmdump --mode upstream:http://example.com:8081
```

如果你想通过把 mitmproxy 放在另一个代理设备前面来串联代理，可以使用 mitmproxy 的上游
模式。在上游模式下，所有请求都会无条件地转交给你指定的上游代理。

{{< figure src="/schematics/proxy-modes-upstream.png" >}}

在上游代理模式下，mitmproxy 同时支持显式 HTTP 和显式 HTTPS。理论上你可以把多个 mitmproxy
实例串成一串，但实际上这没有任何意义（也就是说，除了我们的测试之外）。

## SOCKS 代理 {#socks-proxy}

```shell
mitmdump --mode socks5
```

在这个模式下，mitmproxy 表现为一个 SOCKS5 代理。
它与常规代理模式类似，只是与代理建立连接时使用 SOCKS5 而不是 HTTP。


## DNS 服务器 {#dns-server}

```shell
mitmdump --mode dns
```

这个模式会监听进来的 DNS 查询，并使用你操作系统的解析能力来返回应答。对于 A/AAAA 查询，
你可以选择用
[`dns_use_hosts_file`]({{< relref "/concepts/options" >}}#dns_use_hosts_file)
选项忽略系统的 hosts 文件。用于查询的自定义域名服务器可以通过
[`dns_name_servers`]({{< relref "/concepts/options" >}}#dns_name_servers)
选项指定。默认使用 53 端口。要指定其他端口，比如 5353，请使用 `--mode dns@5353`。
