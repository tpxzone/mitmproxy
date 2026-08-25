---
title: "重放请求"
weight: 4
url: /mitmproxytutorial-replayrequests/
has_asciinema: true
---

# 重放请求 {#replay-requests}

mitmproxy 的另一个强大功能是重放此前的 flow。
它支持两种重放：

* **客户端重放：** mitmproxy 重放此前的客户端请求，也就是把同样的请求再发给服务器一次。
* **服务端重放：** 对于匹配某个先前录制过的请求的请求，mitmproxy 重放对应的服务器响应。

本教程聚焦于更常见的客户端重放场景。
关于[服务端重放]({{< relref "/overview/features#server-side-replay" >}})的更多信息请参见文档。

{{% asciicast file="mitmproxy_replay_requests" poster="0:3" instructions=true %}}

本教程你已经快完成了。在最后一步，你会看到更多值得探索的 mitmproxy 相关资源。
