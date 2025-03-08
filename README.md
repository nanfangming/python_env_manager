### 使用方法:

1. 将代码另存为 `python_env_manager.py`
2. 安装依赖：这个程序只使用了标准库，不需要安装额外依赖
3. 运行程序：`python python_env_manager.py`

※. 若运行时报错：_无法获取Conda环境列表：Command'['cmd.exe'，‘/c’，'conda.exe envlist]
returned non-zero exit status：1_ ，
   最简单粗暴的办法：请把第345行代码 return "conda.exe"  删除掉.exe 改为 return "conda"

### 程序功能介绍:

#### 基础环境管理（第一个选项卡）:

- 显示所有现有的基础环境
- 创建新的基础Python环境，可指定Python版本和基础包
- 删除现有环境

#### 项目环境管理（第二个选项卡）:

- 基于选定的基础环境创建项目专用环境(venv或virtualenv)
- 可选择性地安装requirements.txt文件中的依赖
- 一键激活环境（打开终端并自动激活环境）
- 删除不需要的项目环境

#### 工具与设置（第三个选项卡）:

- 生成快速启动脚本，便于激活环境
- 导出环境列表到JSON文件
- 清理Conda缓存，节省磁盘空间
- 设置Conda可执行文件路径

程序会自动保存配置，记住基础环境和项目环境的信息，方便下次使用。你可以根据自己的需求进一步增强或调整它的功能。
