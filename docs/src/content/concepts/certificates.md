---
title: "证书"
weight: 3
aliases:
  - /concepts-certificates/
---

# 关于证书 {#about-certificates}

只要客户端信任 mitmproxy 内置的证书颁发机构，mitmproxy 就能实时解密加密流量。通常这意味着
必须在客户端设备上安装 mitmproxy 的 CA 证书。

## 快速安装 {#quick-setup}

安装 mitmproxy CA 证书最简单的方式，无疑是使用内置的证书安装应用。做法是：启动 mitmproxy，
在目标设备上配置好正确的代理设置。然后在设备上打开浏览器，访问魔法域名
[mitm.it](http://mitm.it/)。你应该会看到类似这样的界面：

{{< figure src="/certinstall-webapp.png" class="has-border" >}}

点击对应的图标，按照你所在平台的安装说明操作，就可以开始使用了。

## mitmproxy 证书颁发机构 {#the-mitmproxy-certificate-authority}

mitmproxy 首次运行时，会在配置目录（默认是 `~/.mitmproxy`）中创建一个证书颁发机构（CA）
的密钥。这个 CA 用于为每个访问过的网站实时生成伪造证书。
由于你的浏览器默认不会信任 mitmproxy CA，你要么在每个域名上都点掉一次 TLS 证书警告，
要么安装一次 CA 证书让它被信任。

会创建下列文件：

| 文件名                | 内容                                                             |
| --------------------- | ---------------------------------------------------------------- |
| mitmproxy-ca.pem      | PEM 格式的证书**以及私钥**。                                     |
| mitmproxy-ca-cert.pem | PEM 格式的证书。在大多数非 Windows 平台上分发时使用这个。        |
| mitmproxy-ca-cert.p12 | PKCS12 格式的证书。用于 Windows。                                |
| mitmproxy-ca-cert.cer | 与 .pem 相同的文件，但扩展名是某些 Android 设备所要求的。        |

出于安全原因，mitmproxy CA 是在首次启动时唯一生成的，不会在不同设备的 mitmproxy 安装之间
共享。这确保了其他 mitmproxy 用户无法拦截你的流量。

### 手动安装 mitmproxy CA 证书 {#installing-the-mitmproxy-ca-certificate-manually}

有时候没法使用[快速安装应用](#quick-setup)，你需要手动安装 CA。下面列出了一些常见平台
手动安装证书文档的指引。mitmproxy CA 证书在 mitmproxy 首次启动生成之后位于 `~/.mitmproxy`。

- 命令行下的 curl：  
  `curl --proxy 127.0.0.1:8080 --cacert ~/.mitmproxy/mitmproxy-ca-cert.pem https://example.com/`
- 命令行下的 wget：  
  `wget -e https_proxy=127.0.0.1:8080 --ca-certificate ~/.mitmproxy/mitmproxy-ca-cert.pem https://example.com/`
- [macOS](https://support.apple.com/guide/keychain-access/add-certificates-to-a-keychain-kyca2431/mac)
- [macOS（自动化）](https://www.dssw.co.uk/reference/security.html)：
  `sudo security add-trusted-cert -d -p ssl -p basic -k /Library/Keychains/System.keychain ~/.mitmproxy/mitmproxy-ca-cert.pem`
- [Ubuntu/Debian]( https://askubuntu.com/questions/73287/how-do-i-install-a-root-certificate/94861#94861)
- [Fedora](https://docs.fedoraproject.org/en-US/quick-docs/using-shared-system-certificates/#proc_adding-new-certificates)
- [Arch Linux](https://wiki.archlinux.org/title/Transport_Layer_Security#Add_a_certificate_to_a_trust_store)
- [Mozilla Firefox](https://wiki.mozilla.org/MozillaRootCertificate#Mozilla_Firefox)
- [Linux 上的 Chrome](https://stackoverflow.com/a/15076602/198996)
- [iOS](http://jasdev.me/intercepting-ios-traffic)  
  在较新的 iOS 版本上，你还需要为 mitmproxy 根证书启用完全信任：
    1. 进入「设置 > 通用 > 关于本机 > 证书信任设置」。
    2. 在「针对根证书启用完全信任」下，打开对 mitmproxy 证书的信任。
- iOS 模拟器
  1. 确保运行模拟器的 macOS 机器在其网络设置中已配置为使用 mitmproxy。
  2. 在模拟器上打开 Safari，访问 `mitm.it` 下载 iOS 证书。
  3. 进入「设置 > 通用 > VPN 与设备管理」安装该证书。
  4. 进入「设置 > 关于本机 > 证书信任设置」，为已安装的根证书启用信任。
- [Java](https://docs.oracle.com/cd/E19906-01/820-4916/geygn/index.html)：  
  `sudo keytool -importcert -alias mitmproxy -storepass changeit -keystore $JAVA_HOME/lib/security/cacerts -trustcacerts -file ~/.mitmproxy/mitmproxy-ca-cert.pem`
- [Android / Android 模拟器](http://wiki.cacert.org/FAQ/ImportRootCert#Android_Phones_.26_Tablets)
- [Windows](https://web.archive.org/web/20160612045445/http://windows.microsoft.com/en-ca/windows/import-export-certificates-private-keys#1TC=windows-7)
- [Windows（自动化）](https://technet.microsoft.com/en-us/library/cc732443.aspx)：  
  `certutil -addstore root mitmproxy-ca-cert.cer`

### 上游证书嗅探 {#upstream-certificate-sniffing}

当 mitmproxy 收到建立 TLS 的请求（以 ClientHello 消息的形式）时，它会先挂住客户端，
自己先连一次上游服务器，“嗅探”其 TLS 证书的内容。
获得的信息——Common Name、Organization、Subject Alternative Name——随后被用来实时生成一张
由 mitmproxy CA 签名的新拦截证书。接着 mitmproxy 回到客户端，用这张新伪造的证书继续握手。

上游证书嗅探默认开启，也可以通过关闭 `upstream_cert` 选项来禁用。

### 证书固定 {#certificate-pinning}

有些应用采用[证书固定](https://en.wikipedia.org/wiki/HTTP_Public_Key_Pinning)来防止中间人
攻击。这意味着不修改这些应用，它们就不会接受 **mitmproxy** 的证书。
如果这些连接的内容并不重要，建议使用
[ignore_hosts]({{< relref "/howto/ignore-domains">}}) 功能来阻止 **mitmproxy** 拦截发往这些
特定域名的流量。如果你想拦截这些被固定的连接，就需要手动给应用打补丁。对于 Android 和
（已越狱的）iOS 设备，有多种工具可以做到这一点：

 - [apk-mitm](https://github.com/shroudedcode/apk-mitm) 是一个命令行应用，可以自动从
   Android APK 文件中移除证书固定。
 - [objection](https://github.com/sensepost/objection) 是一个由 Frida 驱动的移动端运行时
   探索工具包，支持在 iOS 和 Android 上绕过证书固定。
 - [ssl-kill-switch2](https://github.com/nabla-c0d3/ssl-kill-switch2) 是一个黑盒工具，
   用于在 iOS 和 macOS 应用中禁用证书固定。
 - [android-unpinner](https://github.com/mitmproxy/android-unpinner) 会修改 Android APK，
   注入 Frida 和 HTTP Toolkit 的反固定脚本。

*欢迎使用本页右上角的“在 GitHub 上编辑”按钮推荐其他有用的工具。*

## 使用自定义服务器证书 {#using-a-custom-server-certificate}

你可以通过给 mitmproxy 传入 `--certs [domain=]path_to_certificate` 选项来使用自己的
（叶子）证书。这样 mitmproxy 就会用提供的证书来拦截指定域名，而不是生成一张由它自己的 CA
签名的证书。

证书文件需要是 PEM 格式。你可以把中间证书紧接着叶子证书一起放进去，于是你的 PEM 文件大致
长这样：

    -----BEGIN PRIVATE KEY-----
    <private key>
    -----END PRIVATE KEY-----
    -----BEGIN CERTIFICATE-----
    <cert>
    -----END CERTIFICATE-----
    -----BEGIN CERTIFICATE-----
    <intermediary cert (optional)>
    -----END CERTIFICATE-----

举例来说，你可以用下面的方法生成这种格式的证书：

```bash
openssl genrsa -out cert.key 2048
# （把要中间人的域名填为 Common Name，例如 \*.google.com）
openssl req -new -x509 -key cert.key -out cert.crt
cat cert.key cert.crt > cert.pem
```

现在，你可以用生成的证书运行 mitmproxy：

**对所有域名**

```bash
mitmproxy --certs *=cert.pem
```

**对特定域名**

```bash
mitmproxy --certs *.example.com=cert.pem
```

**注意：** `*.example.com` 针对的是所有子域名。你也可以用 `www.example.com` 来指定某一个
具体子域名。

## 使用自定义证书颁发机构 {#using-a-custom-certificate-authority}

默认情况下，mitmproxy 会用 `~/.mitmproxy/mitmproxy-ca.pem` 作为证书颁发机构，为所有没有
提供自定义证书（见上文）的域名生成证书。你可以通过给 mitmproxy 传入
`--set confdir=DIRECTORY` 选项来使用自己的证书颁发机构。此时 mitmproxy 会在指定目录中
查找 `mitmproxy-ca.pem`。如果该文件不存在，会自动生成。

`mitmproxy-ca.pem` 证书文件大致要长这样：

    -----BEGIN PRIVATE KEY-----
    <private key>
    -----END PRIVATE KEY-----
    -----BEGIN CERTIFICATE-----
    <cert>
    -----END CERTIFICATE-----

用 `openssl x509 -noout -text -in ~/.mitmproxy/mitmproxy-ca.pem` 查看这张证书时，
它至少应该带有下列 X509v3 扩展，mitmproxy 才能用它来生成证书：

    X509v3 extensions:
        X509v3 Key Usage: critical
            Certificate Sign
        X509v3 Basic Constraints: critical
            CA:TRUE

例如，使用 OpenSSL 时，你可以这样创建一个 CA：

```shell
openssl req -x509 -new -nodes -key ca.key -sha256 -out ca.crt -addext keyUsage=critical,keyCertSign
cat ca.key ca.crt > mitmproxy-ca.pem
```

## 双向 TLS（mTLS）与客户端证书 {#mutual-tls-mtls-and-client-certificates}

TLS 的典型用法是：客户端在握手期间用服务器的证书验证服务器身份，而服务器并不通过 TLS 协议
验证客户端身份。相反，客户端是在已建立的安全通道上传输 cookie 或其他访问令牌来完成自身认证。

双向 TLS（mTLS）是这样一种模式：服务器不用 cookie 或访问令牌，而是用客户端在 TLS 握手期间
出示的证书来验证客户端身份。有了 mTLS，客户端和服务器双方都用证书来相互认证。

如果服务器想用 mTLS 验证客户端身份，它会在握手期间额外向客户端发送一条
`CertificateRequest` 消息。客户端随后出示自己的证书，并用匹配的签名证明自己持有对应私钥。
这部分和服务器认证的工作方式完全一样，只是方向反过来。

### mitmproxy 与上游服务器之间的 mTLS {#mtls-between-mitmproxy-and-upstream-server}

你可以通过给 mitmproxy 传入 `--set client_certs=DIRECTORY|FILE` 选项来使用客户端证书。
使用目录时可以按主机名挑选证书，而使用文件名则表示所有 TLS 连接都用同一张指定证书。
证书文件必须是 PEM 格式，且应同时包含未加密的私钥和证书。

你可以给 `--set client_certs=DIRECTORY` 指定一个目录，此时会按文件名查找匹配的证书。
也就是说，如果你访问 example.org，mitmproxy 会在指定目录中查找名为 `example.org.pem` 的
文件，并把它当作客户端证书使用。

### 客户端与 mitmproxy 之间的 mTLS {#mtls-between-client-and-mitmproxy}

默认情况下，mitmproxy 不会向连上来的客户端发送 `CertificateRequest` TLS 握手消息。
这是因为它会让某些并不预期收到证书请求的客户端出问题（最出名的是旧版 Android）。不过，
也有一些客户端——尤其是 MQTT / IoT 环境中的客户端——确实预期收到证书请求，否则 TLS 握手就会
失败。

要让 mitmproxy 向连上来的客户端请求客户端证书，你可以传入 `--set request_client_cert=True`
选项。这会生成一条 `CertificateRequest` TLS 握手消息，并（在成功时）建立 mTLS 连接。
这个选项只是向客户端请求证书，并不会以任何方式校验对方出示的身份。对于测试和开发客户端及
服务器软件的场景，这通常不是问题。如果你在可能有不受信任客户端连入的环境中运行 mitmproxy，
你需要自行采取防护措施。

`request_client_cert` 选项通常与 `client_certs` 搭配使用，像这样：

```bash
mitmproxy --set request_client_cert=True --set client_certs=client-cert.pem
```
