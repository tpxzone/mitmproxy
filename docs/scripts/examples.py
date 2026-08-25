#!/usr/bin/env python3
import re
from pathlib import Path

here = Path(__file__).absolute().parent
example_dir = here / ".." / "src" / "examples" / "addons"
examples = example_dir.glob("*.py")

overview = []
listings = []

for example in examples:
    code = example.read_text()
    slug = str(example.with_suffix("").relative_to(example_dir))
    slug = re.sub(r"[^a-zA-Z]", "-", slug)
    match = re.search(
        r'''
        ^
        (?:[#][^\n]*\n)?  # there might be a shebang
        """
        \s*
        (.+?)
        \s*
        (?:\n\n|""")     # stop on empty line or end of comment
    ''',
        code,
        re.VERBOSE,
    )
    if match:
        comment = " — " + match.group(1)
    else:
        comment = ""
    overview.append(f"  * [{example.name}](#{slug}){comment}\n")
    listings.append(
        f"""
<h3 id="{slug}">示例：{example.name}</h3>

```python
{code.strip()}
```
"""
    )

print(
    f"""
# 插件示例

### 专门的示例插件

{"".join(overview)}

### 内置插件

mitmproxy 自身的许多功能都定义在
[一整套内置插件](https://github.com/mitmproxy/mitmproxy/tree/main/mitmproxy/addons)中，
从禁用缓存协商、粘性 Cookie 这类功能，一直到我们的引导安装 Web 应用，全都是这样实现的。
这些内置插件很值得一读，你会很快发现相当复杂的功能常常可以归结为一个非常小、完全自包含的模块。


### 更多社区示例

由 mitmproxy 社区贡献的更多示例可以
[在 GitHub 上](https://github.com/mitmproxy/mitmproxy/tree/main/examples/contrib)找到。

-------------------------

{"".join(listings)}
"""
)
