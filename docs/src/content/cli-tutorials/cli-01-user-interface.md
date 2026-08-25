---
title: "用户界面"
weight: 1
url: /mitmproxytutorial-userinterface/
has_asciinema: true
---

# 用户界面 {#user-interface}

首先，我们需要熟悉一下 mitmproxy 的用户界面。
打开你启动 mitmproxy 的那个终端窗口。
你现在处于 mitmproxy 的默认视图，它显示的是一个 flow 列表。
你应该能看到浏览器为加载本教程而发出的 HTTP 请求。
每有新请求进来，mitmproxy 就会往视图里添加一行。

{{% asciicast file="mitmproxy_user_interface" poster="0:3" instructions=true %}}

在下一课中，你将学习如何在请求发往服务器之前拦截它们。
