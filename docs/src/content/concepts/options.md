---
title: "选项"
weight: 5
aliases:
  - /concepts-options/
---

# 选项 {#options}

各个 mitmproxy 工具共用一份位于 `~/.mitmproxy/config.yaml` 的
[YAML](http://yaml.org/) 配置文件。这个文件控制的是**选项**——决定 mitmproxy 行为的带类型
的值。选项机制非常全面——事实上，mitmproxy 的所有运行时行为都由选项控制。大多数命令行参数
只是底层选项的别名，而在 **mitmproxy** 和 **mitmweb** 中交互式修改设置，其实只是改变了我们
运行时选项存储中的值。这意味着 mitmproxy 行为的几乎每一个方面都可以通过选项来控制。

选项的权威参考是 `--options` 参数，每个 mitmproxy 工具都暴露了它。传入该参数会把一份带
注解的 YAML 配置打印到控制台，其中包含所有选项及其默认值。

选项机制是可扩展的——第三方插件可以定义选项，其待遇与 mitmproxy 自带的选项完全相同。
这意味着插件也可以通过中央配置文件来配置，并且它们的选项会出现在交互式工具的选项编辑器里。

## 工具 {#tools}

**mitmproxy** 和 **mitmweb** 都内置了编辑器，让你可以查看和操作 mitmproxy 的完整配置状态。
你交互式修改的值会在正在运行的实例中立即生效，也可以通过把设置保存到 YAML 配置文件来持久化
（具体做法请参见对应工具的交互式帮助）。

对所有工具而言，都可以用 `--set` 命令行选项按名称直接设置选项。用法请参见命令行帮助
（`--help`）。例如：
```
mitmproxy --set anticomp=true
mitmweb --set ignore_hosts=example.com --set ignore_hosts=example.org 
```

## 可用选项 {#available-options}

这个列表可能并不反映你当前 mitmproxy 环境中实际可用的内容。要获取最新列表，请对各个
mitmproxy 工具使用 `--options` 参数。

{{< readfile file="/generated/options.html" >}}
