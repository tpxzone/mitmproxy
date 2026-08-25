---
title: "Android 模拟器的系统 CA"
weight: 4
aliases:
  - /howto-install-system-trusted-ca-android/
---

# 在 Android 模拟器上安装系统 CA 证书 {#install-system-ca-certificate-on-android-emulator}
从 Android 7 起，[应用会忽略用户提供的证书](https://android-developers.googleblog.com/2016/07/changes-to-trusted-certificate.html)，
除非它们被显式配置为使用这些证书。由于大多数应用并不主动选择使用用户证书，我们需要把
mitmproxy CA 证书放进系统证书库，以免不得不给每一个想监控的应用打补丁。

请注意，应用可以选择忽略系统证书库，自行维护 CA 证书。这种情况下你还是得给应用打补丁。

## 1. 前置条件 {#1-prerequisites}

- 已安装 [Android Studio / Android SDK](https://developer.android.com/studio)
  （在 Linux 64 位的 4.1.3 版本上测试过）
- 已创建一个 Android 虚拟设备（AVD）。搭建文档见[这里](https://developer.android.com/studio/run/managing-avds)
  - 生产版 AVD（那些标有 “Google Play” 的镜像）会让你无法使用 `adb root`。如果你需要装有
    Google Play，就得改用 [Magisk 方案]({{< ref "#instructions-when-using-magisk" >}})。
  - AVD 的代理设置已配置为使用 mitmproxy。文档见[这里](https://developer.android.com/studio/run/emulator-networking#proxy)

- 已把 Android SDK 中的 emulator 和 adb 可执行文件加入 $PATH 变量
  - 在 Linux 系统上，emulator 通常位于 `/home/<your_user_name>/Android/Sdk/emulator/emulator`
  - 在 Linux 系统上，adb 通常位于 `/home/<your_user_name>/Android/Sdk/platform-tools/adb`
  - 我在自己的 `.bashrc` 里加了这几行
  ``` bash
  export PATH=$PATH:$HOME/Android/Sdk/platform-tools
  export PATH=$PATH:$HOME/Android/Sdk/emulator
  ```

- 已生成 mitmproxy CA 证书
  - 在 Linux 系统上通常位于 `~/.mitmproxy/mitmproxy-ca-cert.cer`
  - 如果该目录为空或不存在，运行一次 `mitmproxy` 以生成证书

## 2. 重命名证书 {#2-rename-certificate}

Android 中的 CA 证书是以其哈希值命名存储的，扩展名为 '0'（例如：`c8450d0d.0`）。你必须算出
自己 CA 证书的哈希值，并把证书复制成以该哈希为文件名的文件。否则 Android 会忽略这张证书。
默认情况下，mitmproxy CA 证书位于这个文件：`~/.mitmproxy/mitmproxy-ca-cert.cer`


### 操作步骤 {#instructions}

- 进入你的证书目录：`cd ~/.mitmproxy/`
- 生成哈希并复制证书：``hashed_name=`openssl x509 -inform PEM -subject_hash_old -in mitmproxy-ca-cert.cer | head -1` && cp mitmproxy-ca-cert.cer $hashed_name.0``

## 3. 把证书放进系统证书库 {#3-insert-certificate-into-system-certificate-store}

现在我们要把 CA 证书放到 Android 文件系统中位于 `/system/etc/security/cacerts/` 的系统证书库
里。默认情况下，`/system` 分区是以只读方式挂载的。下面几步说明如何获得 `/system` 分区的写
权限，以及如何复制[上一步]({{< ref "#2-rename-certificate" >}})中创建的证书。

### 使用 Magisk 时的操作步骤 {#instructions-when-using-magisk}
如果你想使用生产版镜像（标有 “Google Play”，即那些装有 Google Play 的镜像），可以用 Magisk
在 AVD 中获取 root。
[Magisk](https://github.com/topjohnwu/Magisk) 可以让你的 Android 设备或模拟器获得 root。

在 AVD 上安装 Magisk 的[说明见这里](https://gitlab.com/newbit/rootAVD)。
注意：说明里让你启动 AVD。此时不要给 mitmproxy 传 `-http-proxy` 指令。

做完之后，你的模拟器就允许 root 了。你可以打开一个终端模拟器输入 `su` 来验证。
Magisk 应该会询问你是否要给该程序授予 root。授予之后，输入 `whoami` 会显示 `root`。

不过，安装 Magisk 之后，你就不能再用 `-writable-system` 启动模拟器了，那会导致启动循环。
（用 `-show-kernel` 启动 AVD 可以看到错误。）
但你可以把 mitmproxy 证书放进一个 Magisk 模块并安装该模块，从而完成安装。
Magisk 会在启动时负责把你的证书复制到 `/system/etc/security/cacerts/`。

#### 从 mitmweb 下载 Magisk 模块 {#downloading-the-magisk-module-from-mitmweb}
如果你运行的是 mitmweb，可以直接下载 Magisk 模块，而不用手工制作。
停掉你的 AVD，然后用 `-http-proxy 127.0.0.1:8080`（或你运行 mitmweb 代理所用的 IP 和端口
组合）重新启动它。

然后，在 AVD *内部*打开浏览器，访问 `http://mitm.it/cert/magisk`。
系统会提示你下载 `mitmproxy-magisk-module.zip`，这就是你需要的 Magisk 模块。把该文件存到
某个位置（比如 'Downloads'）。

接着打开 Magisk，点击 `Modules` 安装你的模块。

重启你的 AVD。

#### 自行创建包含证书的 Magisk 模块 {#creating-the-magisk-module-containing-your-certificate}
如果你没有运行 mitmweb，就需要自己创建一个 Magisk 模块。
关于 Magisk 模块的深入信息见
[这里](https://topjohnwu.github.io/Magisk/guides.html#magisk-modules)，但基本上归结为以下几步：

创建下列目录：
- `mitmproxycert`（这将是你模块的根目录）
- `mitmproxycert/com/google/android`
- `mitmproxycert/system/etc/security/cacerts`

把[第 2 步]({{< ref "#2-rename-certificate" >}})中重命名过的证书放进
`mitmproxycert/system/etc/security/cacerts`，并对其执行 `chmod 664`。

把 [https://github.com/topjohnwu/Magisk/blob/master/scripts/module_installer.sh](https://github.com/topjohnwu/Magisk/blob/master/scripts/module_installer.sh)
的内容保存为本地文件 `update-binary`，放进 `mitmproxycert/com/google/android`。

创建一个名为 `updater-script` 的文件，其中只包含字符串 `#MAGISK`，放进
`mitmproxycert/com/google/android`。

创建一个名为 `module.prop` 的文件，放进 `mitmproxycert`。文件内容大致如下：

```
id=mitmproxycert
name=MITM proxy certificate
version=1
versionCode=1
author=mitmproxycert
description=My shiny MITM proxy certificate to reveal all secrets and obtain world domination!
```

用类似 `cd ./mitmproxycert ; zip -r ./../mitmproxycert.zip ./` 的命令把模块打包成 zip，
然后用 `adb push ./../mitmproxycert.zip /storage/emulated/0/Download/` 推送到正在运行的 AVD。

然后回到 AVD，打开 Magisk，点击 `Modules` 安装你的模块（可以在 Downloads 目录里找到它）。

重启你的 AVD。

### API LEVEL > 28 时使用 `-writable-system` 的操作步骤 {#instructions-for-api-level--28-using--writable-system}
默认情况下，`/system` 分区是以只读方式挂载的。下面几步说明如何获得 `/system` 分区的写权限，
以及如何复制第 2 章中创建的证书。

从 API LEVEL 29（Android 10）开始，似乎已经无法把 “/” 分区挂载为可读写。Google 用 OverlayFS
提供了一个[针对该问题的变通方案](https://android.googlesource.com/platform/system/core/+/master/fs_mgr/README.overlayfs.md)。
不幸的是，在撰写本文时（2021 年 4 月 11 日），按该变通方案的说明操作会让你的模拟器卡在
[启动循环](https://issuetracker.google.com/issues/144891973)里。Stack Overflow 上有位聪明人
[找到了办法](https://stackoverflow.com/questions/60867956/android-emulator-sdk-10-api-29-wont-start-after-remount-and-reboot)，
无论如何都能让 `/system` 目录可写。

**记住：** 如果你想使用自己的证书，就必须每次都用 `-writable-system` 选项启动模拟器。
否则 Android 会加载一个“干净的”系统镜像。

在运行 API LEVEL 29 和 30 的模拟器上测试过

 #### 操作步骤 {#instructions-1}
   - 列出你的 AVD：`emulator -list-avds`（如果结果是空列表，请在 Android Studio 的
     AVD Manager 里新建一个 AVD）
   - 启动目标 AVD：`emulator -avd <avd_name_here> -writable-system`
     （加 `-show-kernel` 参数可查看内核日志）
   - 以 root 重启 adb：`adb root`
   - 禁用安全启动校验：`adb shell avbctl disable-verification`
   - 重启设备：`adb reboot`
   - 以 root 重启 adb：`adb root`
   - 把分区重新挂载为可读写：`adb remount`。（如果 adb 告诉你需要重启，就再
     `adb reboot` 一次，然后重新运行 `adb remount`。）
   - 推送[第 2 步]({{< ref "#2-rename-certificate" >}})中重命名过的证书：
     `adb push <path_to_certificate> /system/etc/security/cacerts`
   - 设置证书权限：`adb shell chmod 644 /system/etc/security/cacerts/<name_of_pushed_certificate>`
   - 重启设备：`adb reboot`

### API LEVEL <= 28 时使用 `-writable-system` 的操作步骤 {#instructions-for-api-level--28-using--writable-system-1}

在运行 API LEVEL 26、27 和 28 的模拟器上测试过

**记住：** 如果你想使用自己的证书，就必须每次都用 `-writable-system` 选项启动模拟器。
否则 Android 会加载一个“干净的”系统镜像。

   - 列出你的 AVD：`emulator -list-avds`（如果结果是空列表，请在 Android Studio 的
     AVD Manager 里新建一个 AVD）
   - 启动目标 AVD：`emulator -avd <avd_name_here> -writable-system`
     （加 `-show-kernel` 参数可查看内核日志）
   - 以 root 重启 adb：`adb root`
   - 把分区重新挂载为可读写：`adb remount`。（如果 adb 告诉你需要重启，就再
     `adb reboot` 一次，然后重新运行 `adb remount`。）
   - 推送[第 2 步]({{< ref "#2-rename-certificate" >}})中重命名过的证书：
     `adb push <path_to_certificate> /system/etc/security/cacerts`
   - 设置证书权限：`adb shell chmod 644 /system/etc/security/cacerts/<name_of_pushed_certificate>`
   - 重启设备：`adb reboot`

### 验证证书已从系统证书库加载 {#testing-that-your-certificate-is-loaded-from-the-system-certificate-store}

在你的 AVD 中，进入「设置 → 安全 → 高级 → 加密与凭据 → 受信任的凭据」。在列表中找到你的
证书（默认名称是 `mitmproxy`）。
