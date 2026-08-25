---
title: "过滤表达式"
weight: 4
aliases:
  - /concepts-filters/
---

# 过滤表达式 {#filter-expressions}

mitmproxy 中的许多命令都会用到过滤表达式。过滤表达式由下列运算符组成：

{{< readfile file="/generated/filters.html" >}}

- 正则表达式采用 Python 风格。
- 正则表达式可以写成带引号的字符串。
- 包含圆括号、空白字符，或 `~`、`'`、`"` 字符的正则表达式必须加引号，因为这些字符被过滤
  表达式语法保留。否则表达式可能被解析成别的含义，或者直接被拒绝。例如应写
  ~u "get(Info|Routers)"。
- 正则表达式默认不区分大小写。[^1]
- 头部匹配（~h、~hq、~hs）是针对形如 "name: value" 的字符串进行的。
- 不含任何运算符的字符串会与请求 URL 进行匹配。
- 默认的二元运算符是 &。

[^1]: 可以通过设置环境变量 `MITMPROXY_CASE_SENSITIVE_FILTERS=1` 来禁用这一行为。

## 视图 flow 选择器 {#view-flow-selectors}

在交互式场景中，mitmproxy 提供了一组便捷的 flow 选择器，作用于当前视图：

<table class="table filtertable"><tbody>
<tr><th>@all</th><td>所有 flow</td></tr>
<tr><th>@focus</th><td>当前聚焦的 flow</td></tr>
<tr><th>@shown</th><td>当前显示的所有 flow</td></tr>
<tr><th>@hidden</th><td>当前隐藏的所有 flow</td></tr>
<tr><th>@marked</th><td>所有已标记的 flow</td></tr>
<tr><th>@unmarked</th><td>所有未标记的 flow</td></tr>
</tbody></table>

它们在命令和按键绑定中经常用到。

## 示例 {#examples}

URL 中包含 "google.com"：

    google\.com

请求体中包含字符串 "test" 的请求：

    ~q ~b test

除内容类型为 text/html 的请求之外的一切：

    !(~q & ~t "text/html")

替换请求中整个 GET 字符串（必须加引号才能生效）：

    ":~q ~m GET:.*:/replacement.html"
