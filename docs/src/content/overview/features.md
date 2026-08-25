---
title: "功能特性"
weight: 4
aliases:
  - /overview-features/
---

# 功能特性 {#features}

- [Anticache（禁用缓存协商）](#anticache)
- [Blocklist（阻断列表）](#blocklist)
- [客户端重放](#client-side-replay)
- [Map Local（映射到本地）](#map-local)
- [Map Remote（映射到远端）](#map-remote)
- [修改消息体](#modify-body)
- [修改头部](#modify-headers)
- [代理认证](#proxy-authentication)
- [服务端重放](#server-side-replay)
- [Sticky Auth（粘性认证）](#sticky-auth)
- [Sticky Cookies（粘性 Cookie）](#sticky-cookies)
- [流式传输](#streaming)

## Anticache（禁用缓存协商） {#anticache}

当设置了 `anticache` 选项时，mitmproxy 会移除那些可能让服务器返回 `304 Not Modified`
响应的头部（`if-none-match` 和 `if-modified-since`）。当你想确保完整地抓到一次 HTTP
交互时，这非常有用。它也常在客户端重放时使用，以确保服务器返回完整的数据。

## Blocklist（阻断列表） {#blocklist}

使用 `block_list` 选项，你可以阻断特定的网站或请求。此时 mitmproxy 会返回一个固定的
HTTP 状态码，或者干脆不返回任何响应。

`block_list` 的模式形如：

```
/flow-filter/status-code
```

* **flow-filter** 是可选的 mitmproxy [过滤表达式]({{< relref "/concepts/filters">}})，
  用于描述哪些请求应该被阻断。
* **status-code** 是 mitmproxy 为被阻断的请求返回的
  [HTTP 状态码](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)。
  特殊状态码 444 会让 mitmproxy 直接“挂断”，完全不发送任何响应。

<em>分隔符</em>是任意的，由第一个字符决定。

#### 示例 {#examples}

模式 | 说明
------- | -----------
`:~d google-analytics.com:404` | 阻断所有到 google-analytics.com 的请求，并改为返回 “404 Not Found”。
`:~d example.com$:444` | 阻断所有到 example.com 的请求，且不发送 HTTP 响应。
`:!~d ^example\.com$:403` | 只允许发往 *example.com* 的 HTTP 请求。注意这在面对主动攻击者时并不安全，可以被绕过，例如切换到非 HTTP 协议。

## 客户端重放 {#client-side-replay}

客户端重放正如其名：你提供一份先前保存的 HTTP 会话，mitmproxy 会逐条重放其中的客户端
请求。注意 mitmproxy 会串行化这些请求，在开始下一个请求之前会等待服务器的响应。这可能
与录制时的会话不同——录制时的请求可能是并发发出的。

你可能会想把客户端重放和 `anticache` 选项配合使用，以确保服务器返回完整的数据。

## Map Local（映射到本地） {#map-local}

`map_local` 选项让你可以指定任意数量的模式，把 HTTP 请求重定向到本地文件或目录。
mitmproxy 会取本地文件而不是原始资源，并透明地返回给客户端。

`map_local` 的模式形如：

```
|url-regex|local-path
|flow-filter|url-regex|local-path
```

* **local-path** 是应当返回给客户端的文件或目录。

* **url-regex** 是作用于请求 URL 的正则表达式。只有匹配成功才会发生重定向。

* **flow-filter** 是可选的 mitmproxy [过滤表达式]({{< relref "/concepts/filters">}})，
用于进一步限定哪些请求会被重定向。

<em>分隔符</em>是任意的，由第一个字符决定（上例中是 `|`）。


#### 示例 {#examples-1}

模式 | 说明
------- | -----------
`\|example.com/main.js\|~/main-local.js` | 把 `example.com/main.js` 替换为 `~/main-local.js`。
`\|example.com/static\|~/static` | 把 `example.com/static/foo/bar.css` 替换为 `~/static/foo/bar.css`。
`\|example.com/static/foo\|~/static` | 把 `example.com/static/foo/bar.css` 替换为 `~/static/bar.css`。
`\|~m GET\|example.com/static\|~/static` | 把 `example.com/static/foo/bar.css` 替换为 `~/static/foo/bar.css`（但只对 GET 请求生效）。

### 细节 {#details}

如果 *local-path* 是一个文件，那么始终返回该文件。文件的改动会立即生效，不做任何缓存。

如果 *local-path* 是一个目录，那么 *url-regex* 会被用来把请求 URL 切成两部分，右半部分
（不含查询字符串）追加到 *local-path* 之后。
不过，如果 *url-regex* 中包含正则捕获组，行为就会改变：追加的是第一个捕获组的内容
（且此时不会去掉查询字符串）。
特殊字符会被映射为 `_`。如果找不到文件，就会追加 `/index.html` 再试一次。无法通过目录
穿越访问最初指定目录之外的内容。

为了说明这一点，请看下面这个例子：它把所有对 `example.org/css*` 的请求映射到本地目录
`~/static-css`。

<pre>
                  ┌── url regex ──┬─ local path ─┐
map_local option: |<span style="color:#f92672">example.com/css</span>|<span style="color:#82b719">~/static-css</span>
                   <!--                     -->         │
                   <!--                     -->         │    URL 在此处被切分
                   <!--                     -->         ▼            ▼
HTTP Request URL: https://<span style="color:#f92672">example.com/css</span><span style="color:#66d9ef">/print/main.css</span><span style="color:#bbb">?timestamp=123</span>
                          <!--                     -->               <!--                            -->      │        <!--                         -->        ▼
                          <!--                     -->               <!--                            -->      ▼        <!--                         -->      查询字符串被忽略
Served File:      Preferred: <span style="color:#82b719">~/static-css</span><span style="color:#66d9ef">/print/main.css</span>
                   Fallback: <span style="color:#82b719">~/static-css</span><span style="color:#66d9ef">/print/main.css</span>/index.html
                  Otherwise: 404 响应，无内容
</pre>

如果文件取决于查询字符串，我们可以使用正则捕获组。在下面这个例子中，所有对
`example.org/index.php?page=<page-name>` 的 `GET` 请求都被映射到 `~/static-dir/<page-name>`：

<pre>
                    flow
                  ┌filter┬─────────── url regex ───────────┬─ local path ─┐
map_local option: |~m GET|<span style="color:#f92672">example.com/index.php\\?page=</span><span style="color:#66d9ef">(.+)</span>|<span style="color:#82b719">~/static-dir</span>
                          <!--                     -->  │                          <!--                            --> │
                          <!--                     -->  │                          <!--                            --> │ 正则捕获组 = 后缀
                          <!--                     -->  ▼                          <!--                            --> ▼
HTTP Request URL: https://<span style="color:#f92672">example.com/index.php?page=</span><span style="color:#66d9ef">aboutus</span></span>
                          <!--                     -->                           <!--                            -->   │
                          <!--                     -->                           <!--                            -->   ▼
Served File:                 Preferred: <span style="color:#82b719">~/static-dir</span>/<span style="color:#66d9ef">aboutus</span>
                              Fallback: <span style="color:#82b719">~/static-dir</span>/<span style="color:#66d9ef">aboutus</span>/index.html
                             Otherwise: 404 响应，无内容
</pre>

## Map Remote（映射到远端） {#map-remote}

`map_remote` 选项让你可以指定任意数量的模式，在 HTTP 请求 URL 被发往服务器之前对其进行
替换。mitmproxy 会取替换后的 URL 而不是原始资源，并把对应的 HTTP 响应透明地返回给客户端。
`map_remote` 的模式形如：

```
|flow-filter|url-regex|replacement
|url-regex|replacement
```

* **flow-filter** 是可选的 mitmproxy [过滤表达式]({{< relref "/concepts/filters">}})，
用于指定 `map_remote` 选项作用于哪些请求。

* **url-regex** 是一个合法的 Python 正则表达式，定义请求 URL 中哪些部分会被替换。

* **replacement** 是用于替换的字符串字面量。

<em>分隔符</em>是任意的，由第一个字符决定（上例中是 `|`）。

#### 示例 {#examples-2}

把所有以 `.jpg` 结尾的请求映射到 `https://placedog.net/640/480?random`。

```
|.*\.jpg$|https://placedog.net/640/480?random
```

把所有发往 `example.org` 的 GET 请求改道到 `mitmproxy.org`（用 `|` 作为分隔符）：

```
|~m GET|//example.org/|//mitmproxy.org/
```

## 修改消息体 {#modify-body}

`modify_body` 选项让你可以指定任意数量的模式，对 flow 的消息体进行替换。
`modify_body` 的模式形如：

```
/flow-filter/body-regex/replacement
/flow-filter/body-regex/@file-path
/body-regex/replacement
/body-regex/@file-path
```

* **flow-filter** 是可选的 mitmproxy [过滤表达式]({{< relref "/concepts/filters">}})，
用于指定替换作用于哪些 flow。

* **body-regex** 是一个合法的 Python 正则表达式，定义哪些内容会被替换。

* **replacement** 是用于替换的字符串字面量。如果这个字符串以 `@` 开头（形如
`@file-path`），它会被当作一个**文件路径**，替换内容将从该文件读取。

<em>分隔符</em>是任意的，由第一个字符决定（上例中是 `/`）。

修改钩子会在收到客户端请求或服务器响应时触发。只有匹配的那部分 flow 会受影响：例如，
如果修改钩子是在服务器响应时触发的，那么替换只会作用于 Response 对象，Request 保持不变。
你可以通过过滤模式来控制钩子是在请求、响应还是两者上触发。如果你需要比这更精细的控制，
可以很容易地写一个脚本，直接使用 Flow 各组成部分上的替换 API。消息体的修改对流式传输的
消息体无效，详情请参见[流式传输]({{< relref "#streaming" >}})。

#### 示例 {#examples-3}

把请求体中的 `foo` 替换为 `bar`：

```
/~q/foo/bar
```

把 `foo` 替换为从 `~/xss-exploit` 读取的数据：

```bash
mitmdump --modify-body :~q:foo:@~/xss-exploit
```

## 修改头部 {#modify-headers}

`modify_headers` 选项让你可以指定一组要修改的头部。可以新增头部，也可以覆盖或删除已有
头部。`modify_headers` 的模式形如：

```
/flow-filter/name/value
/flow-filter/name/@file-path
/name/value
/name/@file-path
```

* **flow-filter** 是可选的 mitmproxy [过滤表达式]({{< relref "/concepts/filters">}})，
用于指定在哪些 flow 上修改头部。

* **name** 是要设置、替换或删除的头部名称。

* **value** 是要设置或替换的头部值。**value** 为空表示删除名为 **name** 的已有头部。
如果这个值字符串以 `@` 开头（形如 `@file-path`），它会被当作一个**文件路径**，替换内容
将从该文件读取。

<em>分隔符</em>是任意的，由第一个字符决定（上例中是 `/`）。

默认情况下会覆盖已有头部。这一行为可以通过过滤表达式来改变。

修改钩子会在收到客户端请求或服务器响应时触发。只有匹配的那部分 flow 会受影响：例如，
如果修改钩子是在服务器响应时触发的，那么替换只会作用于 Response 对象，Request 保持不变。
你可以通过过滤模式来控制钩子是在请求、响应还是两者上触发。如果你需要比这更精细的控制，
可以很容易地写一个脚本，直接使用 Flow 各组成部分上的替换 API。

#### 示例 {#examples-4}

把所有请求的 `Host` 头部设置为 `example.org`（已有的 `Host` 头部会被替换）：

```
/~q/Host/example.org
```

只对没有 `Host` 头部的请求，把 `Host` 头部设置为 `example.org`：

```
/~q & !~h Host:/Host/example.org
```

把所有请求的 `User-Agent` 头部设置为从 `~/useragent.txt` 读取的数据
（已有的 `User-Agent` 头部会被替换）：

```
/~q/User-Agent/@~/useragent.txt
```

删除所有请求中已有的 `Host` 头部：

```
/~q/Host/
```

## 代理认证 {#proxy-authentication}

`proxyauth` 选项会在用户被允许使用代理之前要求其进行认证。认证头部会从 flow 中剥离，
因此不会被传递给上游服务器。目前只支持 HTTP Basic 认证。

按设计，代理认证在透明代理模式下无法很好地工作，因为客户端并不知道自己在与代理通信。
mitmproxy 会对每一个域名分别重新请求凭据。
SOCKS 代理认证目前尚未实现
（[#738](https://github.com/mitmproxy/mitmproxy/issues/738)）。

## 服务端重放 {#server-side-replay}

`server_replay` 选项让我们可以从已保存的 HTTP 会话中重放服务器响应。为此，我们使用一套
启发式规则把收到的请求与已保存的响应进行匹配。默认情况下，在把收到的请求与重放文件中的
响应做匹配时，我们会排除请求头部，只用 URL 和请求方法来匹配。这在大多数情况下都能工作，
并且使得在请求头部本身会自然变化的场景下（例如使用了不同的 user agent）依然可以重放
服务器响应。

定制匹配启发式规则的方式非常多，包括指定要纳入匹配的头部、要排除的请求参数等等。这些
选项都收敛在 `server_replay` 前缀下——详情请参见内置文档。

### 响应刷新 {#response-refreshing}

不加修改地直接重放服务器响应往往会导致意料之外的行为。例如，录制会话时还在未来的 cookie
过期时间，到重放时可能已经成为过去。默认情况下，mitmproxy 会在把服务器响应发给客户端之前
先刷新它们。**date**、**expires** 和 **last-modified** 头部都会被更新，使其保持与录制时
相同的相对时间偏移。也就是说，如果它们在录制时处于过去，那么在重放时也处于过去，反之亦然。
Cookie 的过期时间也以类似方式更新。

你可以把 `server_replay_refresh` 选项设为 `false` 来关闭这一行为。

## Sticky auth（粘性认证） {#sticky-auth}

`stickyauth` 选项与 sticky cookie 选项类似：一旦看到过 HTTP **Authorization** 头部，
就会把它重放给服务器。这足以让你通过代理、使用 HTTP Basic 认证访问服务器资源。注意
<span data-role="program">mitmproxy</span>（暂）不支持重放 HTTP Digest 认证。

## Sticky cookies（粘性 Cookie） {#sticky-cookies}

当设置了 `stickycookie` 选项时，**mitmproxy** 会把服务器最近设置的 cookie 添加到所有不带
cookie 的请求上。设想有这样一个服务：认证之后它会设置一个 cookie 来跟踪会话。使用 sticky
cookie，你可以启动 mitmproxy，然后像平常那样用浏览器完成该服务的认证。认证之后，你就可以
像访问免认证资源那样通过 mitmproxy 请求需要认证的资源，因为 mitmproxy 会自动把会话跟踪
cookie 加到请求上。除此之外，这还让你可以（用 wget 或 curl 之类的工具）脚本化地与需要
认证的资源交互，而无需操心认证问题。

sticky cookie 与[客户端重放]({{< relref "#client-side-replay" >}})配合使用时尤其强大——
你可以把认证过程录制一次，然后在每次需要与受保护资源交互时，启动时直接重放它即可。

## 流式传输 {#streaming}

默认情况下，mitmproxy 会读取整个请求/响应，对其执行指定的各种操作，然后再把消息发给
对方。在下载或上传大文件时，这可能会成为问题。启用流式传输后，消息体不会在代理上缓冲，
而是直接发往服务器/客户端。这目前意味着消息体在 mitmproxy 中不可访问，对消息体的修改也
不会生效。HTTP 头部仍然会在发送前完整缓冲。

请求/响应的流式传输是通过在 `stream_large_bodies` 选项中指定一个大小阈值来启用的。

### 定制流式传输 {#customizing-streaming}

你也可以用脚本来精确定制哪些请求或响应走流式传输。把 Request/Response 的 ``.stream``
属性设为 ``True``，即可将其标记为流式传输：

{{< example src="examples/addons/http-stream-simple.py" lang="py" >}}
