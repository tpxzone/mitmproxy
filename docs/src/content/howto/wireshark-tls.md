---
title: "Wireshark 与 SSL/TLS"
weight: 1
aliases:
  - /howto-wireshark-tls/
---

# Wireshark 与 SSL/TLS 主密钥 {#wireshark-and-ssltls-master-secrets}

mitmproxy 可以把 SSL/TLS 主密钥记录下来，这样外部程序就能解密进出代理的 SSL/TLS 连接。
较新版本的 Wireshark 可以用这些日志文件来解密数据包。更多信息请参见
[Wireshark wiki](https://wiki.wireshark.org/TLS#using-the-pre-master-secret)。

设置环境变量 `SSLKEYLOGFILE` 指向一个可写的文本文件即可启用密钥记录：

```bash
SSLKEYLOGFILE="$PWD/.mitmproxy/sslkeylogfile.txt" mitmproxy
```

你也可以 `export` 这个环境变量，让它对当前 shell 会话启动的所有应用都持续生效。

在 Wireshark 中，可以通过 `Edit -> Preferences -> Protocols -> TLS ->
(Pre)-Master-Secret log filename` 指定密钥文件路径。如果你的 SSLKEYLOGFILE 还不存在，
先建一个空文本文件即可，这样才能在 Wireshark 里选中它（或者先运行 mitmproxy 来创建文件并
收集主密钥）。

注意，`SSLKEYLOGFILE` 也会被其他程序识别，例如 Firefox 和 Chrome。如果这带来了麻烦，
你可以改用 `MITMPROXY_SSLKEYLOGFILE`，这样就不会影响其他应用。
