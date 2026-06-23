@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║      🚀 智能物流系统 - 本地启动（推荐方案）🚀               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查Docker
echo [1/6] 检查Docker环境...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker运行正常
echo.

REM 启动MySQL和Redis
echo [2/6] 启动数据库服务（MySQL + Redis）...
cd /d "%~dp0docker"
docker compose up -d mysql redis
if errorlevel 1 (
    echo ❌ 数据库启动失败
    pause
    exit /b 1
)
echo ✅ 数据库服务已启动
echo.

REM 等待数据库就绪
echo [3/6] 等待数据库就绪...
echo     MySQL正在初始化（约30秒）...
timeout /t 30 /nobreak >nul
echo ✅ 数据库就绪
echo.

REM 检查Maven
echo [4/6] 检查后端环境...
where mvn >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 未检测到Maven，请确保已安装Maven
    echo    或使用IDEA直接运行LogisticsApplication
    pause
    exit /b 1
)
echo ✅ Maven已安装
echo.

REM 启动后端
echo [5/6] 启动后端服务...
cd /d "%~dp0backend"
start "物流系统-后端" cmd /k "echo 🚀 后端启动中... && echo. && mvn clean spring-boot:run"
echo ✅ 后端正在启动（新窗口）
echo    等待20秒后端启动...
timeout /t 20 /nobreak >nul
echo.

REM 启动前端
echo [6/6] 启动前端服务...
cd /d "%~dp0frontend"
start "物流系统-前端" cmd /k "echo 🚀 前端启动中... && echo. && npm run dev"
echo ✅ 前端正在启动（新窗口）
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎊 系统启动完成！
echo.
echo 📋 访问地址:
echo    前端: http://localhost:5173
echo    后端: http://localhost:8080
echo    Swagger: http://localhost:8080/swagger-ui/index.html
echo.
echo 📋 数据库连接:
echo    MySQL: localhost:3306 (root/logistics2026)
echo    Redis: localhost:6379
echo.
echo 📋 测试账号:
echo    管理员: admin / 123456
echo    运营员: operator / 123456
echo    访客: guest / 123456
echo.
echo 📊 查看日志:
echo    后端: 查看"物流系统-后端"窗口
echo    前端: 查看"物流系统-前端"窗口
echo    数据库: docker logs logistics-mysql
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 提示:
echo    • 后端和前端在独立窗口运行
echo    • 可以实时查看运行日志
echo    • 关闭窗口即停止对应服务
echo    • 热重载: 代码修改自动生效
echo.
echo 🛑 停止服务:
echo    • 关闭后端/前端窗口
echo    • 运行: docker compose down
echo.
pause
