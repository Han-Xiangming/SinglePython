<!--suppress ALL -->

<div align=center><img src="Icon.ico" width="  "></div>
<h1 align="center" name="binpython">SinglePython</h1>
<p align="center">
    <em>SinglePython 是一个轻量级的 Python 解释器，可以作为命令行工具或 Windows Start 菜单快捷方式使用。它提供了一个简单的交互式 shell 和一些有用的功能，如导入自定义库、执行指定的 Python 文件等。
</em>
</p>
<p align="center">

<img alt="Github stars" src="https://img.shields.io/github/stars/Han-Xiangming/SinglePython.svg"/>
<img alt="pyver" src="https://img.shields.io/badge/PythonVersion-&gt;3.12-green"/>
<img alt="license" src="https://img.shields.io/badge/LICENSE-AGPL--3.0-brightgreen"/>

### BiliBili: https://space.bilibili.com/669743441

# 用法

```
用法: SinglePython [OPTIONS]

Options:
-f <filename> --file=<filename>    输入 Python 文件名并运行 （*.py）
-h            --help               查看帮助
-v            --version            查看SinglePython版本
```

# 构建

1. 克隆此项目

```bash
git clone https://github.com/Han-Xiangming/SinglePython
cd SinglePython
```

2. 安装依赖

```bash
pip install -r .\requirement.txt
```

3. 构建 SinglePython
 ```bash
 pyinstaller  -y main.spec
 ```

## 联系我们

如果您在使用 SinglePython 过程中遇到任何问题或有任何建议，请通过以下方式与我们联系：

- 发送电子邮件到 2728513634@qq.com。
- 在 [GitHub](https://github.com/Han-Xiangming/SinglePython/issues) 上新建一个 issue。 
