---
title: "拦截请求"
weight: 2
url: /mitmproxytutorial-interceptrequests/
has_asciinema: true
---

# 拦截请求 {#intercept-requests}

mitmproxy 的一个强大功能是拦截请求。
被拦截的请求会被暂停，这样用户就可以在发往服务器之前修改（或丢弃）它。
mitmproxy 的 `set intercept` 命令用于配置拦截。
该命令默认绑定到快捷键 `i`。

拦截*所有*请求通常不是你想要的，因为那会不断打断你的浏览。
因此，mitmproxy 要求 `set intercept` 的第一个参数是一个
[flow 过滤表达式]({{< relref "/concepts/filters" >}})，以便有选择地拦截请求。
在下面的教程中，我们使用 flow 过滤器 `~u <regex>`，它通过把正则表达式与请求的 URL 做匹配来
筛选 flow。

{{% asciicast file="mitmproxy_intercept_requests" poster="0:3" instructions=true %}}

在下一课中，你将学习如何在把被拦截的 flow 发往服务器之前修改它们。
