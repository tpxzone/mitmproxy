---
title: "事件钩子"
weight: 2
# this is important so that the relative links in the generated file work.
url: api/events.html
aliases:
    - /addons-events/
---

# 事件钩子 {#event-hooks}

插件通过事件钩子挂接到 mitmproxy 的内部机制。这些钩子在插件上以一组约定名称的方法实现。
许多事件会把 `Flow` 对象作为参数传入——通过修改这些对象，插件就能实时改变流量。例如，
下面这个插件会添加一个响应头部，记录已见过的响应数量：

{{< example src="examples/addons/http-add-header.py" lang="py" >}}

## 可用钩子 {#available-hooks}

下面这些插件列出了所有可用的事件钩子。

{{< readfile file="/generated/api/events.html" >}}
