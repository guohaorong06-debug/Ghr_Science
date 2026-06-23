@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║      🚀 智能物流系统 - Docker完整部署 🚀                    ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 进入docker目录
cd /d "%~dp0"

REM 检查Docker
echo [1/8] 检查Docker环境...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo ✅ Docker运行正常
echo.

REM 清理旧容器
echo [2/8] 清理旧容器...
docker compose down >nul 2>&1
echo ✅ 旧容器已清理
echo.

REM 删除旧镜像
echo [3/8] 删除旧后端镜像...
docker rmi docker-backend >nul 2>&1
echo ✅ 旧镜像已删除
echo.

REM 构建后端镜像
echo [4/8] 构建后端镜像（需要2-3分钟）...
echo     正在下载依赖和编译代码...
docker compose build backend
if errorlevel 1 (
    echo.
    echo ❌ 后端镜像构建失败
    echo.
    echo 💡 建议:
    echo    1. 检查网络连接
    echo    2. 或使用本地启动: start-local.bat
    echo    3. 查看详细错误: docker compose build backend --no-cache
    echo.
    pause
    exit /b 1
)
echo ✅ 后端镜像构建成功
echo.

REM 启动所有服务
echo [5/8] 启动所有服务...
docker compose up -d
if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)
echo ✅ 服务启动命令执行成功
echo.

REM 等待服务启动
echo [6/8] 等待服务初始化...
echo     MySQL正在初始化...
timeout /t 30 /nobreak >nul
echo ✅ 数据库初始化完成
echo.

REM 检查容器状态
echo [7/8] 检查容器状态...
docker ps -a --filter "name=logistics-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM 检查后端日志
echo [8/8] 检查后端启动日志...
timeout /t 5 /nobreak >nul
docker logs logistics-backend --tail 30
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 🎊 部署完成！
echo.
echo 📋 服务状态:
docker ps --filter "name=logistics-" --format "  {{.Names}}: {{.Status}}"
echo.
echo 📋 访问地址:
echo    前端: http://localhost
echo    后端: http://localhost:8080
echo    Swagger: http://localhost:8080/swagger-ui/index.html
echo.
echo 📋 测试账号:
echo    管理员: admin / 123456
echo    运营员: operator / 123456
echo    访客: guest / 123456
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 💡 实用命令:
echo    查看后端日志: docker logs -f logistics-backend
echo    查看前端日志: docker logs -f logistics-frontend
echo    查看所有日志: docker compose logs -f
echo    停止所有服务: docker compose down
echo    重启后端: docker restart logistics-backend
echo.
echo 🔍 如果后端无法访问:
echo    1. docker logs logistics-backend
echo    2. docker restart logistics-backend
echo    3. 或使用本地启动: ..\start-local.bat
echo.
pause
