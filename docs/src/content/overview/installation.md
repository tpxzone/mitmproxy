---
title: "安装"
weight: 2
aliases:
  - /overview-installation/
---

# 安装 {#installation}

请按照适用于你的操作系统的步骤操作。

## macOS

在 macOS 上安装 mitmproxy 的推荐方式是使用
[Homebrew](https://brew.sh/)：

```bash
brew install --cask mitmproxy
```

此外，你也可以从 [mitmproxy.org](https://mitmproxy.org/) 下载独立的二进制文件。

## Linux

在 Linux 上安装 mitmproxy 的推荐方式是从 [mitmproxy.org](https://mitmproxy.org/)
下载独立的二进制文件。

一些 Linux 发行版通过其原生软件仓库提供由社区维护的 mitmproxy 包（例如 Arch Linux、
Debian、Ubuntu、Kali Linux、OpenSUSE 等）。我们不参与下游打包工作的维护，而这些包往往
落后于当前的 mitmproxy 版本。原生包相关的问题请直接联系仓库维护者。

## Windows

要在 Windows 上安装 mitmproxy，请从 [mitmproxy.org](https://mitmproxy.org/) 下载安装程序。
另外，mitmproxy 也可以在
[Microsoft Store](https://apps.microsoft.com/detail/9NWNDLQMNZD7) 上获取，它会自动安装更新。
我们同样提供独立的二进制文件，但它们的启动时间要长得多，因为需要先把一些文件解压到临时目录。
安装完成后，mitmproxy、mitmdump 和 mitmweb 也会被加入你的 PATH，可以从命令行调用。

我们强烈建议[安装 Windows Terminal](https://aka.ms/terminal)，以改善控制台界面的渲染效果。

所有 mitmproxy 工具在
[WSL（Windows Subsystem for Linux）](https://docs.microsoft.com/en-us/windows/wsl/about)
下也都受支持。[安装 WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10) 之后，
按照 Linux 的 mitmproxy 安装说明操作即可。

## 进阶安装 {#advanced-installation}

### 开发环境搭建 {#development-setup}

如果你想直接从源代码或 GitHub main 分支安装 mitmproxy，请参见 GitHub 上的
[CONTRIBUTING.md](https://github.com/mitmproxy/mitmproxy/blob/main/CONTRIBUTING.md)。

### 从 Python 包索引（PyPI）安装 {#installation-from-the-python-package-index-pypi}

如果你的 mitmproxy 插件需要安装额外的 Python 包，你可以从
[PyPI](https://pypi.org/project/mitmproxy/) 安装 mitmproxy。

虽然可选方案很多[^1]，但我们推荐使用 uv 来安装：

[^1]: 如果你熟悉 Python 生态，就会知道安装 Python 包的方式多如牛毛。其中大多数
    （pip、virtualenv、pipenv 等）应该都能正常工作，但我们没有精力为它们提供支持。

1. 安装 [uv](https://docs.astral.sh/uv/)。
2. 执行 `uv tool install mitmproxy`。

要安装额外的 Python 包，请运行 `uv tool install --with <your-package-name> mitmproxy`。

### Docker 镜像 {#docker-images}

你可以使用来自
[DockerHub](https://hub.docker.com/r/mitmproxy/mitmproxy/) 的官方 mitmproxy 镜像。

### 二进制包的安全注意事项 {#security-considerations-for-binary-packages}

我们预编译的二进制包和 Docker 镜像内含一个自包含的 Python 3 环境、较新版本的 OpenSSL，
以及其他若干本来编译安装起来会很麻烦的依赖。

二进制包中的依赖在发布时就已冻结，无法就地更新。这意味着其中可能存在的任何 bug 或安全
问题也会一并被固化下来。我们通常不会仅为了更新依赖而发布新的二进制包（不过如果我们
得知了非常严重的问题，也可能会这么做）。如果你使用我们的二进制包，请确保定期更新，
以保持一切都是最新的。

作为一条基本原则，mitmproxy 不会“回传数据”，因此也不会做任何更新检查。
