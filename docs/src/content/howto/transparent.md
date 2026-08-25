---
title: "透明代理"
weight: 1
aliases:
 - /howto-transparent/
---

# 透明代理 {#transparent-proxying}

使用透明代理时，流量会在网络层被重定向到代理，无需任何客户端配置。这使得透明代理非常适合
那些你无法改变客户端行为的场景——不感知代理的移动应用就是一个常见例子。

{{% note %}}
新的 [WireGuard]({{< relref "/concepts/modes#wireguard" >}})
和[本地抓包]({{< relref "/concepts/modes#local-capture" >}})模式为透明代理提供了另一种
实现方式。它们搭建起来简单得多，因为不需要开启 IP 转发或修改路由规则。
{{% /note %}}

要搭建透明代理，我们需要两个新组件。第一个是重定向机制，它把本应发往互联网上某台服务器的
TCP 连接透明地改道到一个正在监听的代理服务器。这通常表现为与代理服务器同主机的一个防火墙——
Linux 上的 [iptables](http://www.netfilter.org/) 或 OSX 上的
[pf](https://en.wikipedia.org/wiki/PF_(firewall))。当代理收到一个被重定向过来的连接时，
它看到的是一个普通的 HTTP 请求，不带主机信息。这时第二个新组件就派上用场了——一个主机模块，
让我们可以向重定向器查询该 TCP 连接的原始目的地。

目前，mitmproxy 在 OSX Lion 及以上版本，以及所有当前的 Linux 发行版上都支持透明代理。

## Linux

在 Linux 上，mitmproxy 与 iptables 的重定向机制集成来实现透明模式。

### 1. 开启 IP 转发。 {#1-enable-ip-forwarding}

```bash
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
```

这确保你的机器会转发数据包而不是拒绝它们。

如果你希望重启后依然生效，需要调整 `/etc/sysctl.conf` 或新建一个
`/etc/sysctl.d/mitmproxy.conf`（参见[这里](https://superuser.com/a/625852)）。

### 2. 禁用 ICMP 重定向。 {#2-disable-icmp-redirects}

```bash
sysctl -w net.ipv4.conf.all.send_redirects=0
```

如果你的测试设备在同一个物理网络里，你的机器不应该告诉该设备“绕过代理有更短的路径可走”。

如果你希望重启后依然生效，参见上文。

### 3. 创建一套 iptables 规则，把目标流量重定向到 mitmproxy。 {#3-create-an-iptables-ruleset-that-redirects-the-desired-traffic-to-mitmproxy}

具体细节会因你的环境而异，但规则集大致应该长这样：

```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080
ip6tables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
ip6tables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080
```

如果你希望重启后依然生效，可以使用 `iptables-persistent` 包（参见
[这里](http://www.microhowto.info/howto/make_the_configuration_of_iptables_persistent_on_debian.html)）。

### 4. 启动 mitmproxy。 {#4-fire-up-mitmproxy}

你大概会想用这样一条命令：

```bash
mitmproxy --mode transparent --showhost
```

`--mode transparent` 选项开启透明模式，`--showhost` 参数告诉 mitmproxy 用 Host 头部的值来
显示 URL。

### 5. 最后，配置你的测试设备。 {#5-finally-configure-your-test-device}

把测试设备的默认网关设置为运行 mitmproxy 的那台主机，并
[在测试设备上安装 mitmproxy 证书颁发机构]({{< relref "/concepts/certificates" >}})。

### 重定向本机自身发出的流量的变通办法 {#work-around-to-redirect-traffic-originating-from-the-machine-itself}

按上文完成第 **1、2** 步，但*不要*执行第 **3** 步中的命令，而是执行下面这些

创建一个用来运行 mitmproxy 的用户

```bash
sudo useradd --create-home mitmproxyuser
sudo -u mitmproxyuser -H bash -c 'cd ~ && pip install --user mitmproxy'
```

然后配置 iptables 规则，把本机的所有流量重定向到 mitmproxy。**注意**，这些命令一执行，
在你启动 mitmproxy *之前*就无法成功发起网络请求了。如果遇到问题，`iptables -t nat -F`
是一种简单粗暴的方式，可以清空 iptables `nat` 表中的*所有*规则（包括你配置过的其他规则）。

```bash
iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner mitmproxyuser --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner mitmproxyuser --dport 443 -j REDIRECT --to-port 8080
ip6tables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner mitmproxyuser --dport 80 -j REDIRECT --to-port 8080
ip6tables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner mitmproxyuser --dport 443 -j REDIRECT --to-port 8080
```

这会把机器上除 `mitmproxyuser` 之外所有用户的数据包重定向到 mitmproxy。为了避免形成回环，
请以 `mitmproxyuser` 用户身份运行 mitmproxy。因此第 **4** 步应该长这样：

```bash
sudo -u mitmproxyuser -H bash -c '$HOME/.local/bin/mitmproxy --mode transparent --showhost --set block_global=false'
```

## OpenBSD

### 1. 开启 IP 转发。 {#1-enable-ip-forwarding-1}

```bash
sudo sysctl -w net.inet.ip.forwarding=1
```

### 2. 把下面两行放进 **/etc/pf.conf**。 {#2-place-the-following-two-lines-in-etcpfconf}

```
mitm_if = "re2"
pass in quick proto tcp from $mitm_if to port { 80, 443 } divert-to 127.0.0.1 port 8080
```

这些规则告诉 pf 把来自 `$mitm_if`、目标端口为 80 或 443 的所有流量转向运行在 8080 端口的
本地 mitmproxy 实例。你应该把 `$mitm_if` 的值替换为你的测试设备将出现在的那个网络接口。

### 3. 用这些规则配置 pf。 {#3-configure-pf-with-the-rules}

```bash
doas pfctl -f /etc/pf.conf
```

### 4. 现在启用它。 {#4-and-now-enable-it}

```bash
doas pfctl -e
```

### 5. 启动 mitmproxy。 {#5-fire-up-mitmproxy}

你大概会想用这样一条命令：

```bash
mitmproxy --mode transparent --listen-host 127.0.0.1 --showhost
```

`--mode transparent` 选项开启透明模式，`--showhost` 参数告诉 mitmproxy 用 Host 头部的值来
显示 URL。

### 6. 最后，配置你的测试设备。 {#6-finally-configure-your-test-device}

把测试设备的默认网关设置为运行 mitmproxy 的那台主机，并
[在测试设备上安装 mitmproxy 证书颁发机构]({{< relref "/concepts/certificates" >}})。

{{% note %}}
注意，上面给出的 pf.conf 中的 **divert-to** 规则只作用于入向流量。
**这意味着它们不会重定向来自运行 pf 那台机器本身的流量。** 我们无法区分非 mitmproxy 应用
发出的出向连接和 mitmproxy 自身发出的出向连接——如果你想拦截自己的流量，应该用一台外部主机
来运行 mitmproxy。不过话说回来，pf 足够灵活，能满足各种富有创意的可能性，比如拦截来自虚拟机
的流量。更多内容请参见 **pf.conf** 手册页。
{{% /note %}}

## macOS

OSX Lion 集成了来自 OpenBSD 项目的
[pf](https://en.wikipedia.org/wiki/PF_(firewall)) 包过滤器，mitmproxy 用它在 OSX 上实现
透明模式。注意，这也意味着我们不支持更早版本 OSX 的透明模式。

### 1. 开启 IP 转发。 {#1-enable-ip-forwarding-2}

```bash
sudo sysctl -w net.inet.ip.forwarding=1
```

### 2. 把下面这一行放进一个文件，比如叫 **pf.conf**。 {#2-place-the-following-line-in-a-file-called-say-pfconf}

```
rdr pass on en0 inet proto tcp to any port {80, 443} -> 127.0.0.1 port 8080
```

这条规则告诉 pf 把所有目标端口为 80 或 443 的流量重定向到运行在 8080 端口的本地 mitmproxy
实例。你应该把 `en0` 替换为你的测试设备将出现在的那个网络接口。

### 3. 用这些规则配置 pf。 {#3-configure-pf-with-the-rules-1}

```bash
sudo pfctl -f pf.conf
```

### 4. 现在启用它。 {#4-and-now-enable-it-1}

```bash
sudo pfctl -e
```

### 5. 配置 sudoers，允许 mitmproxy 访问 pfctl。 {#5-configure-sudoers-to-allow-mitmproxy-to-access-pfctl}

以 root 身份编辑系统上的 **/etc/sudoers** 文件。在文件末尾加上下面这一行：

```
ALL ALL=NOPASSWD: /sbin/pfctl -s state
```

注意，这允许系统上任何用户以 root 身份免密执行 `/sbin/pfctl -s state` 命令。它只允许查看
状态表，因此不应构成过分的安全风险。如果你比较讲究，也可以把限制收紧到运行 mitmproxy 的
那个用户。

### 6. 启动 mitmproxy。 {#6-fire-up-mitmproxy}

你大概会想用这样一条命令：

```bash
mitmproxy --mode transparent --showhost
```

`--mode transparent` 参数开启透明模式，`--showhost` 参数告诉 mitmproxy 用 Host 头部的值来
显示 URL。

### 7. 最后，配置你的测试设备。 {#7-finally-configure-your-test-device}

把测试设备的默认网关设置为运行 mitmproxy 的那台主机，并
[在测试设备上安装 mitmproxy 证书颁发机构]({{< relref "/concepts/certificates" >}})。

{{% note %}}
注意，上面给出的 pf.conf 中的 **rdr** 规则只作用于入向流量。
**这意味着它们不会重定向来自运行 pf 那台机器本身的流量。** 我们无法区分非 mitmproxy 应用
发出的出向连接和 mitmproxy 自身发出的出向连接。如果你想拦截自己 macOS 上的流量，
请参见下面的变通办法，或者用一台外部主机来运行 mitmproxy。事实上，PF 足够灵活，
能满足各种富有创意的可能性，比如拦截来自虚拟机的流量。更多内容请参见 **pf.conf** 手册页。
{{% /note %}}

### 重定向本机自身发出的流量的变通办法 {#work-around-to-redirect-traffic-originating-from-the-machine-itself-1}

按上文完成第 **1、2** 步，但在第 **2** 步中把 **pf.conf** 文件的内容改为

```
#The ports to redirect to proxy
redir_ports = "{http, https}"

#The address the transparent proxy is listening on
tproxy = "127.0.0.1 port 8080"

#The user the transparent proxy is running as
tproxy_user = "nobody"

#The users whose connection must be redirected.
#
#This cannot involve the user which runs the
#transparent proxy as that would cause an infinite loop.
#

rdr pass proto tcp from any to any port $redir_ports -> $tproxy
pass out route-to (lo0 127.0.0.1) proto tcp from any to any port $redir_ports user { != $tproxy_user }

# End the file with a blank newline

```

然后按上文完成第 **3-5** 步。这会把机器上除 `nobody` 之外所有用户的数据包重定向到
mitmproxy。为了避免形成回环，请以 `nobody` 用户身份运行 mitmproxy。因此第 **6** 步应该
长这样：

```bash
sudo -u nobody mitmproxy --mode transparent --showhost
```

## Windows

所有命令都需要在 Windows 10 及以上版本中以提升的权限运行。PowerShell 应以管理员身份运行。

### 1. 开启 IP 路由。 {#1-enable-ip-routing}

```batch
reg add HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v IPEnableRouter /D 1 /t REG_DWORD /f
```

这让你的 Windows 能够充当 IP 路由器。现在可以启用 RemoteAccess 服务了。

```batch
sc config RemoteAccess start= demand
```

这条命令启用 IP 路由服务。`demand` 选项允许手动启动该服务。或者，你可以把 `demand` 换成
`auto`，让 IP 路由在开机时启用。

```batch
sc start RemoteAccess
```

启动 RemoteAccess 服务。Windows 现在可以路由 IP 了！

### 2. 阻断出向 ICMP 重定向。 {#2-block-outgoing-icmp-redirect}

```batch
netsh advfirewall firewall add rule name="Don't send ICMP redirects" dir=out protocol=icmpv4:5,any action=block
```

上面这条命令在高级防火墙中加了一条规则，不重定向任何 ICMP 数据包。

如果你的测试设备在同一个物理网络里，你的机器不应该告诉该设备“绕过代理有更短的路径可走”。

### 3. 启动 mitmproxy。 {#3-fire-up-mitmproxy}

你大概会想用这样一条命令：

```batch
mitmproxy --mode transparent --showhost
```

`--mode transparent` 选项开启透明模式，`--showhost` 参数告诉 mitmproxy 用 Host 头部的值来
显示 URL。

### 4. 最后，配置你的测试设备。 {#4-finally-configure-your-test-device}

把测试设备的默认网关设置为运行 mitmproxy 的那台主机，并
[在测试设备上安装 mitmproxy 证书颁发机构]({{< relref "/concepts/certificates" >}})。

## Linux 上的“完全”透明模式 {#full-transparent-mode-on-linux}

{{% note %}}
该功能在 mitmproxy 7 及以上版本中目前不可用
（[#4914](https://github.com/mitmproxy/mitmproxy/discussions/4914)）。
{{% /note %}}

默认情况下，mitmproxy 会用它自己的本地 IP 地址来建立服务端连接。如果这不是你想要的，
可以用 --spoof-source-address 参数，让服务端连接使用客户端的 IP 地址。该模式需要下面这些
配置才能工作：

```bash
CLIENT_NET=192.168.1.0/24
TABLE_ID=100
MARK=1

echo "$TABLE_ID     mitmproxy" >> /etc/iproute2/rt_tables
iptables -t mangle -A PREROUTING -d $CLIENT_NET -j MARK --set-mark $MARK
iptables -t nat \
    -A PREROUTING -p tcp -s $CLIENT_NET \
    --match multiport --dports 80,443 -j \
    REDIRECT --to-port 8080

ip rule add fwmark $MARK lookup $TABLE_ID
ip route add local $CLIENT_NET dev lo table $TABLE_ID
```

不过该模式确实需要 root 权限。examples 目录下有一个名为 'mitmproxy_shim.c' 的包装程序，
可以让你在放弃权限的情况下使用该模式。用法如下：

```bash
gcc examples/complex/full_transparency_shim.c -o mitmproxy_shim -lcap
sudo chown root:root mitmproxy_shim
sudo chmod u+s mitmproxy_shim
./mitmproxy_shim $(which mitmproxy) --mode transparent --set spoof-source-address
```
