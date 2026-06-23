@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ===================================================================
echo.
echo      智能物流系统 - 本地启动
echo.
echo ===================================================================
echo.

REM 检查Docker
echo [1/6] 检查Docker环境...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)
echo SUCCESS: Docker运行正常
echo.

REM 启动MySQL和Redis
echo [2/6] 启动数据库服务（MySQL + Redis）...
cd /d "%~dp0docker"
docker compose up -d mysql redis
if errorlevel 1 (
    echo ERROR: 数据库启动失败
    pause
    exit /b 1
)
echo SUCCESS: 数据库服务已启动
echo.

REM 等待数据库就绪
echo [3/6] 等待数据库初始化（30秒）...
timeout /t 30 /nobreak >nul
echo SUCCESS: 数据库初始化完成
echo.

REM 检查Maven
echo [4/6] 检查后端环境...
where mvn >nul 2>&1
if errorlevel 1 (
    echo WARNING: 未检测到Maven
    echo 请使用IDEA直接运行LogisticsApplication
    pause
    exit /b 1
)
echo SUCCESS: Maven已安装
echo.

REM 启动后端
echo [5/6] 启动后端服务...
cd /d "%~dp0backend"
start "Logistics-Backend" cmd /k "echo Backend starting... && echo. && mvn clean spring-boot:run"
echo SUCCESS: 后端正在启动（新窗口）
echo 等待20秒后端启动...
timeout /t 20 /nobreak >nul
echo.

REM 启动前端
echo [6/6] 启动前端服务...
cd /d "%~dp0frontend"
start "Logistics-Frontend" cmd /k "echo Frontend starting... && echo. && npm run dev"
echo SUCCESS: 前端正在启动（新窗口）
echo.

echo ===================================================================
echo.
echo SUCCESS: 系统启动完成！
echo.
echo 访问地址:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8080
echo    Swagger:  http://localhost:8080/swagger-ui/index.html
echo.
echo 测试账号:
echo    Admin:    admin / 123456
echo    Operator: operator / 123456
echo    Guest:    guest / 123456
echo.
echo 提示:
echo    - 后端和前端在独立窗口运行
echo    - 可以实时查看运行日志
echo    - 关闭窗口即停止对应服务
echo.
echo 停止服务:
echo    - 关闭后端/前端窗口
echo    - 运行: docker compose down
echo.
echo ===================================================================
echo.
pause
