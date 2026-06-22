@echo off
chcp 65001 >nul
echo =========================================
echo 智能物流决策系统 - 一键部署脚本
echo =========================================

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose未安装
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过

cd /d "%~dp0"

echo 🛑 停止旧容器...
docker-compose down

set /p clean="是否清理旧镜像？(y/n): "
if /i "%clean%"=="y" (
    echo 🧹 清理旧镜像...
    docker-compose down --rmi all
)

echo 🔨 构建镜像并启动容器...
docker-compose up -d --build

echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

echo 📊 容器状态：
docker-compose ps

echo.
echo =========================================
echo ✅ 部署完成！
echo =========================================
echo 访问地址：
echo   前端：http://localhost
echo   后端：http://localhost:8080
echo   API文档：http://localhost:8080/swagger-ui/index.html
echo.
echo 默认管理员账号：
echo   用户名：admin
echo   密码：admin123
echo.
echo 查看日志：
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend
echo.
echo 停止服务：
echo   docker-compose down
echo =========================================
pause
