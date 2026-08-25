---
title: "透明代理虚拟机"
weight: 3
aliases:
  - /howto-transparent-vms/
---

# 透明代理虚拟机 {#transparently-proxify-virtual-machines}

本文演示如何用 mitmproxy 搭建透明代理。这个例子里我们使用 VirtualBox 虚拟机，代理机跑
Ubuntu，但这套通用的 *互联网 \<--\> 代理虚拟机 \<--\> （虚拟）内部网络* 结构也可以套用到
其他环境。

## 1. 配置代理虚拟机 {#1-configure-proxy-vm}

首先，我们得弄清 Ubuntu 把我们的网络接口映射成了什么名字。可以用下面的命令查看：

```bash
ip link
```

在 Ubuntu 和 VirtualBox 上，通常 **eth0** 或 **enp0s3**（Ubuntu 15.10 及更新版本）连接
互联网，而 **eth1** 或 **enp0s8**（Ubuntu 15.10 及更新版本）连接将被代理的内部网络，
并配置为使用静态 IP（192.168.3.1）。如果名字不一样，请使用你从 *ip link* 命令得到的名字。

### VirtualBox 配置 {#virtualbox-configuration}

{{< figure src="/transparent-vms/step1_vbox_eth0.png" >}}

{{< figure src="/transparent-vms/step1_vbox_eth1.png" >}}

### 虚拟机网络配置 {#vm-network-configuration}

{{< figure src="/transparent-vms/step1_proxy.png" >}}

## 2. 配置 DHCP 和 DNS {#2-configure-dhcp-and-dns}

我们用 dnsmasq 在内部网络中提供 DHCP 和 DNS。Dnsmasq 是一个轻量级服务器，专为小规模网络
提供 DNS（以及可选的 DHCP 和 TFTP）服务。在此之前，我们得先处理 Ubuntu 的一些怪癖：
**Ubuntu \>12.04** 默认会运行一个内部 dnsmasq 实例（只监听回环）
[\[1\]](https://www.stgraber.org/2012/02/24/dns-in-ubuntu-12-04/)。对我们的场景来说，
需要禁用它——把 **/etc/NetworkManager/NetworkManager.conf** 中的 `dns=dnsmasq` 改为
`#dns=dnsmasq`，然后如果是 Ubuntu 16.04 或更新版本，运行：

```bash
sudo systemctl restart NetworkManager
```

如果是 Ubuntu 12.04 或 14.04，运行：

```bash
sudo restart network-manager
```

即可。

现在可以安装并配置 dnsmasq 了：

```bash
sudo apt-get install dnsmasq
```

把 **/etc/dnsmasq.conf** 替换为下面的配置：

```
# Listen for DNS requests on the internal network
interface=eth1
bind-interfaces
# Act as a DHCP server, assign IP addresses to clients
dhcp-range=192.168.3.10,192.168.3.100,96h
# Broadcast gateway and dns server information
dhcp-option=option:router,192.168.3.1
dhcp-option=option:dns-server,192.168.3.1
```

应用改动：

如果是 Ubuntu 16.04 或更新版本：

```bash
sudo systemctl restart dnsmasq
```

如果是 Ubuntu 12.04 或 14.04：

```bash
sudo service dnsmasq restart
```

此时，内部虚拟网络中的**被代理机器**应该已经通过 DHCP 拿到 IP 地址了：

{{< figure src="/transparent-vms/step2_proxied_vm.png" >}}

## 3. 把流量重定向到 mitmproxy {#3-redirect-traffic-to-mitmproxy}

要把流量重定向到 mitmproxy，我们需要开启 IP 转发并添加两条 iptables 规则：

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 443 -j REDIRECT --to-port 8080
```

## 4. 运行 mitmproxy {#4-run-mitmproxy}

最后，我们可以用下面的命令以透明模式运行 mitmproxy

```bash
mitmproxy --mode transparent
```

被代理的机器无法在 HTTP 或 DNS 请求之外泄漏任何数据。如有需要，你现在可以
[在被代理机器上安装 mitmproxy 证书]({{< relref "/concepts/certificates" >}})。
