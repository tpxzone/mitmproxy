---
title: "客户端重放"
weight: 1
aliases:
  - /tute-clientreplay/
---

# 客户端回放：30 秒示例 {#client-playback-a-30-second-example}

我家附近的咖啡馆用的是一套摇摇欲坠、极不可靠的无线网络，慷慨地由市政委员会花纳税人的钱赞助。
连上之后，你会被重定向到一个受 SSL 保护的页面，要求输入用户名和密码。填完信息之后，你就可以
尽情享受时断时续的掉线、糖浆般的速度，以及配置错误的透明代理了。

这类事情我一有机会就想自动化掉，理由是现在花的时间长远来看肯定能赚回来。放在这个场景里，
我大概会用 [Firebug](https://getfirebug.com/) 把表单 POST 参数和目标 URL 挖出来，
然后打开编辑器，用 Python 的 [urllib](https://docs.python.org/library/urllib.html)
写个小脚本来模拟提交。这一通折腾可不少。而用 mitmproxy，我们真的可以在 30 秒内搞定，
完全不用操心任何细节。做法如下。

## 1. 运行 mitmdump，把我们的 HTTP 会话录制到文件。 {#1-run-mitmdump-to-record-our-http-conversation-to-a-file}

```bash
mitmdump -w wireless-login
```

## 2. 把浏览器指向这个 mitmdump 实例。 {#2-point-your-browser-at-the-mitmdump-instance}

有一个叫 [FoxyProxy](https://addons.mozilla.org/fi/firefox/addon/foxyproxy-standard/)
的 Firefox 扩展，可以让你快速切换是否使用 mitmproxy。这里我假定你已经
[为浏览器配置好了 mitmproxy 的 SSL 证书颁发机构]({{< relref
"/concepts/certificates" >}})。

## 3. 像平常一样登录 {#3-log-in-as-usual}

搞定\！现在你在 wireless-login 文件里有了一份序列化的登录过程，随时可以像这样重放它：

```bash
mitmdump -C wireless-login
```

## 锦上添花 {#embellishments}

到这里其实已经完事了，但如果想的话，还可以做几点润色。我用 [wicd](https://launchpad.net/wicd)
自动加入我常去的无线网络，它允许我指定连接后要执行的命令。我把上面那条客户端重放命令填进去，
瞧\！——完全免手动的无线网络启动。

我们可能还想剔除那些下载 CSS、JS、图片之类的请求。它们只会让重放多花一点点时间，
其实并不必要，而我总莫名地想把它们修剪掉。于是，我们对序列化后的会话启动 mitmproxy 控制台
工具，像这样：

```bash
mitmproxy -r wireless-login
```

现在我们可以逐条手动删除（用 <span data-role="kbd">d</span> 键盘快捷键）想剔除的内容。
完成后，用 <span data-role="kbd">w</span> 把会话保存回文件。
