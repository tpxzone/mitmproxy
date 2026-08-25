---
title: "自定义内容视图"
weight: 6
menu:
    addons:
        weight: 6
---

# 自定义内容视图 {#custom-contentviews}

内容视图（contentview）负责美化打印二进制消息数据（例如 HTTP 响应体），否则这些数据对人类
来说很难看懂。有些内容视图还是<em>交互式</em>的，也就是说美化后的表示可以被编辑，mitmproxy 会把它
重新编码回二进制消息。

## 简单示例 {#simple-example}

所有内容视图都实现 [Contentview] 基类：

{{< example src="examples/addons/contentview.py" lang="py" >}}

要使用这个内容视图，把它当作普通插件加载即可：

```shell
mitmproxy -s examples/addons/contentview.py
```

和其他所有 mitmproxy 插件一样，内容视图在文件内容变化时会被热重载。
mitmproxy（但 mitmweb 不会）还会自动重新渲染该内容视图。

更多细节请参见 [`mitmproxy.contentviews` API 文档]。


## 语法高亮 {#syntax-highlighting}

内容视图始终返回未加样式的 `str`，但它们可以声明自己的输出匹配某个预定义的
[`SyntaxHighlight` 格式]。特别地，二进制格式可以美化成 YAML（或 JSON），并使用 YAML 高亮器。

目前支持的格式列表还比较有限，但实现基于 [tree-sitter]，很容易扩展
（参见 [`mitmproxy-highlight` crate]）。

## 交互式内容视图 {#interactive-contentviews}

下面的例子实现了一个交互式内容视图，允许用户在美化后的表示上进行编辑：

{{< example src="examples/addons/contentview-interactive.py" lang="py" >}}

[`mitmproxy.contentviews` API 文档]: {{< relref "api/mitmproxy.contentviews.md" >}}
[Contentview]: {{< relref "api/mitmproxy.contentviews.md#Contentview" >}}
[`SyntaxHighlight` 格式]: {{< relref "api/mitmproxy.contentviews.md#Contentview.syntax_highlight" >}}
[`mitmproxy-highlight` crate]: https://github.com/mitmproxy/mitmproxy_rs/tree/main/mitmproxy-highlight/src
[tree-sitter]: https://tree-sitter.github.io/tree-sitter/
