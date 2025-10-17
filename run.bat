@echo off
REM Audio Perception - 启动脚本
REM 激活虚拟环境并运行程序

echo 启动 Audio Perception - Dynamic Audio Visualization System
echo ========================================================

REM 切换到项目目录
cd /d "C:\Users\ALIENWARE\Desktop\Poly\5913_Creative_Programming\Tutorials\Audio-Perception"

REM 检查虚拟环境是否存在
if not exist "venv\Scripts\python.exe" (
    echo 错误：虚拟环境未找到。请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境并运行程序
echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 启动程序...
python main.py

REM 如果程序出现错误，暂停以查看错误信息
if %ERRORLEVEL% neq 0 (
    echo.
    echo 程序运行出现错误，错误代码: %ERRORLEVEL%
    pause
)