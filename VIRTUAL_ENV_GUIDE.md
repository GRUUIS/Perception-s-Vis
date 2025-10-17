# Audio Perception - 虚拟环境运行指南

本项目使用Python虚拟环境来管理依赖项。以下是完整的设置和运行指南。

## 环境要求
- Python 3.8 或更高版本
- Windows 操作系统
- 音频设备（麦克风/音频输入）

## 快速开始

### 方法一：使用批处理脚本（推荐）

1. **首次设置环境：**
   ```batch
   双击运行 setup.bat
   ```
   这将：
   - 创建虚拟环境 `venv`
   - 安装所有必需的依赖包
   - 配置项目环境

2. **运行程序：**
   ```batch
   双击运行 run.bat
   ```

### 方法二：手动命令行操作

1. **创建虚拟环境：**
   ```powershell
   cd "C:\Users\ALIENWARE\Desktop\Poly\5913_Creative_Programming\Tutorials\Audio-Perception"
   python -m venv venv
   ```

2. **激活虚拟环境：**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **安装依赖：**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyaudio
   ```

4. **运行程序：**
   ```powershell
   python main.py
   ```

## 已安装的包
- `pyaudio==0.2.14` - 音频捕获和处理
- `numpy>=1.21.0` - 数值计算
- `pygame>=2.1.0` - 图形界面和游戏开发
- `pygame-gui>=0.6.0` - GUI组件

## 虚拟环境说明
- 虚拟环境路径：`venv/`
- Python解释器：`venv\Scripts\python.exe`
- 包管理器：`venv\Scripts\pip.exe`

## 故障排除

### PyAudio安装问题
如果PyAudio安装失败，可以尝试：
```powershell
pip install --upgrade setuptools
pip install pyaudio
```

### 权限问题
如果出现PowerShell执行策略问题：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 音频设备问题
确保系统有可用的音频输入设备（麦克风），程序需要实时音频输入来生成可视化效果。

## 项目结构
```
Audio-Perception/
├── venv/                 # 虚拟环境目录
├── src/                  # 源代码
│   ├── audio/           # 音频分析模块
│   ├── ui/              # 用户界面
│   ├── visualization/   # 可视化引擎
│   └── storage/         # 数据存储
├── data/                # 数据目录（自动创建）
├── main.py              # 主程序入口
├── requirements.txt     # 依赖列表
├── setup.bat           # 环境设置脚本
└── run.bat             # 程序启动脚本
```

## 使用说明
程序启动后会显示欢迎界面，可以选择：
- **Single Mode**: 个人录制模式
- **Multiple Mode**: 多用户画廊模式

程序会实时分析音频输入并生成相应的视觉效果。