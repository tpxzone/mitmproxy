---
title: "快速上手"
weight: 3
aliases:
  - /overview-getting-started/
---

# 快速上手 {#getting-started}

我们假定你已经在机器上[安装]({{< relref "/overview/installation">}})好了 mitmproxy。

## 启动你需要的工具 {#launch-the-tool-you-need}

你可以从命令行 / 终端启动我们的三个工具中的任意一个。

* **mitmproxy** 提供交互式命令行界面
* **mitmweb** 提供基于浏览器的图形界面
* **mitmdump** 提供非交互式的终端输出

## 配置你的浏览器或设备 {#configure-your-browser-or-device}

Mitmproxy 默认以[常规 HTTP 代理]({{< relref
"/concepts/modes#regular-proxy">}})的方式启动，监听 `http://localhost:8080`。

你需要配置浏览器或设备，把所有流量都路由到 mitmproxy。浏览器的版本和配置项经常变动，
因此我们建议你直接在网上搜索如何为你的系统配置 HTTP 代理。有些操作系统提供全局设置，
有些浏览器有自己的设置，还有些应用程序使用环境变量，等等。

你可以访问 http://mitm.it 来确认自己的网络流量确实经过了 mitmproxy——它应该会显示一个
[简单页面]({{< relref "/concepts/certificates#quick-setup">}})，用于安装 mitmproxy 的
证书颁发机构（CA），而这正是下一步要做的事。按照适用于你的操作系统 / 平台的说明安装 CA。

## 验证一切正常工作 {#verifying-everything-works}

此时，你正在运行的 mitmproxy 实例应该已经显示出来自客户端的第一批 HTTP flow 了。你可以
访问 https://mitmproxy.org 来测试所有 TLS 加密的网络流量是否按预期工作——它应该会作为
一条新的 flow 出现，你可以对其进行检查。

## 资源 {#resources}

* [**GitHub**](https://github.com/mitmproxy/mitmproxy)：如果你想提出使用方面的问题、
  为 mitmproxy 贡献代码，或者提交 bug 报告，请使用 GitHub。
