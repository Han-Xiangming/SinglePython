<div align=center><img src="Icon.ico" width="  "></div>
<h1 align="center" name="binpython">SinglePython</h1>
<p align="center">
    <em>Lightweight and small portable Python, build with pyinstaller
</em>
</p>
<p align="center">

![Github stars](https://img.shields.io/github/stars/Han-Xiangming/SinglePython.svg)
![pyver](https://img.shields.io/badge/PythonVersion->3.12-green)
![license](https://img.shields.io/badge/LICENSE-AGPL--3.0-brightgreen)
### BiliBili: https://space.bilibili.com/669743441?spm_id_from=333.1007.0.0


# 用法
```
用法: SinglePython [OPTIONS]

Options:
-f <filename> --file=<filename>    输入 Python 文件名并运行 （*.py），但此选项无运行完成提示
-h            --help               查看帮助
-v            --version            查看SinglePython版本
```
# 构建

1. 克隆此项目
```bash
git clone https://github.com/Han-Xiangming/SinglePython
cd binpython
```
2. 安装Python，Pyinstaller
```bash
pip install pyinstaller
```
3. 构建 SinglePython
   运行build.bat即可



## Configuration files and default startup configuration

Create "startup.conf" in the same level directory, the content of the file is the default startup Python script, such as "startupfile.py", the next time you open binpython, the startup script configured in "startup.conf" will be started by default 

Create "binpython_config" folder including "welcome.py", "version.py", "help.txt", put the startup script every time binpython is opened in "welcome.py", "version.py" will  Displayed when the --help parameter is used, "help.txt" is put into the display text when the -h parameter is used.  If one of the above files is missing or not configured, the default script and text for binpython will be displayed 
