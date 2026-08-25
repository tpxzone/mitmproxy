---
title: "在 Apple GameCenter 上刷高分"
weight: 2
aliases:
  - /tute-highscores/
---

# 在 Apple 的 GameCenter 上刷高分 {#setting-highscores-on-apples-gamecenter}

## 准备工作 {#the-setup}

在这个教程里，我要给你演示用 mitmproxy 创造性地干预 Apple Game Center 流量有多简单。
先做准备：[安装 mitmproxy 根证书]({{< relref "/concepts/certificates" >}})。然后在你的桌面
上启动 mitmproxy，并把 iPhone 配置为使用它作为代理。

## 先看看 Game Center 的流量 {#taking-a-look-at-the-game-center-traffic}

我们先来看一眼 Game Center 的流量。本教程中我要用的游戏是
[Super Mega Worm](https://itunes.apple.com/us/app/super-mega-worm/id388541990?mt=8)——
一款很棒的 iPhone 复古末世横版小游戏：

{{< figure src="/tute-highscores/supermega.png" >}}

打完一局（慢慢来）之后，观察流经 mitmproxy 的流量：

{{< figure src="/tute-highscores/one.png" >}}

我们看到了一堆预料之中的东西——初始化、拉取排行榜等等。然后，就在最后，有一个 POST 发往
这个诱人的 URL：

```
https://service.gc.apple.com/WebObjects/GKGameStatsService.woa/wa/submitScore
```

提交的内容格外有意思：

```xml
<plist version="1.0">
  <dict>
    <key>scores</key>
    <array>
      <dict>
        <key>category</key>
        <string>SMW_Adv_USA1</string>
        <key>context</key>
        <integer>0</integer>
        <key>score-value</key>
        <integer>55</integer>
        <key>timestamp</key>
        <integer>1363515361321</integer>
      </dict>
    </array>
  </dict>
</plist>
```

这是一个 [property list](https://en.wikipedia.org/wiki/Property_list)，里面包含游戏的
标识符、一个分数（本例中是 55），以及一个时间戳。看起来动手脚相当简单。

## 修改并重放分数提交 {#modifying-and-replaying-the-score-submission}

我们来编辑这次分数提交。首先，在 mitmproxy 中选中它，然后按
<span data-role="kbd">enter</span> 查看。确认你看的是请求而不是响应——可以用
<span data-role="kbd">tab</span> 在两者之间切换。现在按 <span data-role="kbd">e</span>
进入编辑。系统会提示你想改请求的哪一部分——按 <span data-role="kbd">r</span> 选择原始消息体。
你偏好的编辑器（取自 EDITOR 环境变量）现在会启动。我们把分数抬到一个更有野心的数字：

```xml
<plist version="1.0">
  <dict>
    <key>scores</key>
    <array>
      <dict>
        <key>category</key>
        <string>SMW_Adv_USA1</string>
        <key>context</key>
        <integer>0</integer>
        <key>score-value</key>
        <integer>2200272667</integer>
        <key>timestamp</key>
        <integer>1363515361321</integer>
      </dict>
    </array>
  </dict>
</plist>
```

保存文件并退出编辑器。

最后一步是重放这个修改过的请求。只需按 <span data-role="kbd">r</span> 进行重放。

## 光辉战果与一点耐人寻味的事 {#the-glorious-result-and-some-intrigue}

{{< figure src="/tute-highscores/leaderboard.png" >}}

就是这样——按记录来说，我是有史以来最强的 Super Mega Worm 玩家。

这个故事还有个奇妙的后记。我最初写这篇教程时，排行榜前列所有竞争者的分数都是同一个：
2,147,483,647（现在已经不是这样了，因为照着本教程作弊的同道太多了）。如果你觉得这个数字
似曾相识，那你没看错：它是 2^31-1，也就是有符号 32 位整数能容纳的最大值。现在我再告诉你
Super Mega Worm 的另一个古怪之处——每局结束时，它提交给 Game Center 的是你此前的最高分，
而不是本局分数。这意味着它把你的最高分存在了某个地方，而我猜它是把那个存下来的分数读回到
一个有符号整数里。所以，如果你**要**用相对朴素的手段作弊——在已越狱的手机上修改存档分数——
那 2^31-1 很可能就是你能拿到的最高分。可反过来说，如果游戏本身就把分数存在有符号 32 位整数
里，那你靠完美操作也能拿到同样的分数，相当于打穿了这个游戏。那么这次到底是哪一种呢？
这就留给你自己判断了。
