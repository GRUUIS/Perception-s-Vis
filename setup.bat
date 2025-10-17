@echo off
REM Audio Perception - 环境设置脚本
REM 创建虚拟环境并安装依赖

echo 设置 Audio Perception 开发环境
echo ================================

REM 切换到项目目录
cd /d "C:\Users\ALIENWARE\Desktop\Poly\5913_Creative_Programming\Tutorials\Audio-Perception"

REM 创建虚拟环境
echo 创建Python虚拟环境...
python -m venv venv

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖包
echo 安装项目依赖包...
pip install -r requirements.txt

REM 额外安装pyaudio（Windows版本）
echo 安装 PyAudio...
pip install pyaudio

echo.
echo 环境设置完成！
echo 现在可以使用 run.bat 启动程序
pause