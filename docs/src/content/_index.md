---
title: "简介"
layout: single
menu:
    overview:
        weight: 1
---

# 简介 {#introduction}

mitmproxy 是一套工具，提供支持 SSL/TLS 的交互式拦截代理，可用于 HTTP/1、HTTP/2 和 WebSocket。

## 功能特性 {#features}

- 拦截 HTTP 与 HTTPS 请求和响应，并实时修改它们
- 保存完整的 HTTP 会话，供后续重放和分析
- 重放 HTTP 会话的客户端部分
- 重放先前录制的服务端 HTTP 响应
- 反向代理模式，把流量转发到指定服务器
- macOS 和 Linux 上的透明代理模式
- 使用 Python 脚本化地修改 HTTP 流量
- 用于拦截的 SSL/TLS 证书实时生成
- 以及[更多更多的功能……]({{< relref "/overview/features">}})

## 三个强大的核心工具 {#3-powerful-core-tools}

mitmproxy 项目的这几个工具其实是一组前端，它们暴露的是同一套底层能力。当我们说
“mitmproxy” 时，通常指这三个工具中的任意一个——它们只是同一个核心代理的不同前端。

**mitmproxy** 是一个支持 SSL/TLS 的交互式拦截代理，带有控制台界面，支持 HTTP/1、HTTP/2 和 WebSocket。

**mitmweb** 是 mitmproxy 的 Web 界面。

**mitmdump** 是 mitmproxy 的命令行版本。可以把它理解为 HTTP 版的 tcpdump。

发行包可以在 [mitmproxy 官网](https://mitmproxy.org)上找到。
开发相关信息和源代码可以在我们的
[GitHub 仓库](https://github.com/mitmproxy/mitmproxy)中找到。

### mitmproxy

{{< figure src="/screenshots/mitmproxy.png" alt="终端界面截图" >}}

**mitmproxy** 是一个控制台工具，允许你交互式地检查和修改 HTTP 流量。它与 mitmdump 的
区别在于：所有 flow 都保存在内存中，因此它适用于抓取和处理规模不大的样本。在
**mitmproxy** 的任意界面按 `?` 快捷键，即可查看与当前上下文相关的文档。

---

### mitmweb

{{< figure src="/screenshots/mitmweb.png" alt="Web 界面截图" >}}

**mitmweb** 是 mitmproxy 基于 Web 的用户界面，允许你交互式地检查和修改 HTTP 流量。
和 mitmproxy 一样，它与 mitmdump 的区别在于所有 flow 都保存在内存中，因此它适用于
抓取和处理规模不大的样本。

{{% note %}}
Mitmweb 目前处于 beta 阶段。对于界面中已经暴露出来的功能，我们认为它是稳定的，
但它仍然缺少许多 mitmproxy 的功能。
{{% /note %}}

---

### mitmdump

**mitmdump** 是 mitmproxy 的命令行搭档。它提供类似 tcpdump 的功能，让你查看、录制并
以编程方式转换 HTTP 流量。完整文档请参见 `--help` 参数的输出。

#### 示例：保存流量 {#example-saving-traffic}

```bash
mitmdump -w outfile
```

以代理模式启动 mitmdump，并把所有流量写入 **outfile**。

#### 过滤已保存的流量 {#filtering-saved-traffic}

```bash
mitmdump -nr infile -w outfile "~m post"
```

启动 mitmdump 但不绑定代理端口（`-n`），从 infile 读取所有 flow，应用指定的过滤
表达式（只匹配 POST），然后写入 outfile。

#### 客户端重放 {#client-replay}

```bash
mitmdump -nC outfile
```

启动 mitmdump 但不绑定代理端口（`-n`），然后重放 outfile 中的所有请求
（`-C filename`）。这些参数可以按显而易见的方式组合，因此你可以从一个文件重放请求，
并把生成的 flow 写入另一个文件：

```bash
mitmdump -nC srcfile -w dstfile
```

更多信息请参见[客户端重放]({{< relref "/overview/features#client-side-replay"
>}})一节。

#### 运行脚本 {#running-a-script}

```bash
mitmdump -s examples/simple/add_header.py
```

这会运行示例脚本 **add_header.py**，它只是给所有响应添加一个新的头部。

#### 脚本化数据转换 {#scripted-data-transformation}

```bash
mitmdump -ns examples/simple/add_header.py -r srcfile -w dstfile
```

这条命令从 **srcfile** 加载 flow，按照指定脚本进行转换，然后写回 **dstfile**。
