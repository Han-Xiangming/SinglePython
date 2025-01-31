# config.py
import configparser
import os


def load_config(config_path='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')
    single_python_info = {
        'version': config.get('SinglePython', 'version'),
        'libs_warning': config.get('SinglePython', 'libs_warning'),
        'releases_version': config.get('SinglePython', 'releases_version'),
        'importlibs': config.get('SinglePython', 'importlibs'),
        'clear_command': "cls" if os.name == "nt" else "clear"
    }
    # print("Loaded configuration:", single_python_info)  # 调试输出
    return single_python_info


SinglePythonInfo = load_config()

# 添加调试输出以验证配置是否正确加载
if __name__ == "__main__":
    print("SinglePythonInfo:", SinglePythonInfo)
