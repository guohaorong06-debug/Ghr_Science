@echo off
REM 简化版启动脚本 - 仅启动数据库和提示

echo.
echo ===================================================================
echo.
echo      Logistics System - Quick Start
echo.
echo ===================================================================
echo.

echo Step 1: Starting MySQL and Redis...
echo.

REM 进入docker目录
if exist "%~dp0docker" (
    cd /d "%~dp0docker"
) else (
    echo ERROR: docker directory not found!
    echo Current directory: %CD%
    echo Script location: %~dp0
    pause
    exit /b 1
)

REM 启动数据库
docker compose up -d mysql redis
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start database services
    echo Please check:
    echo   1. Docker Desktop is running
    echo   2. You are in the correct directory
    pause
    exit /b 1
)

echo.
echo SUCCESS: Database services started
echo.
echo ===================================================================
echo.
echo Next Steps:
echo.
echo 1. Start Backend (Choose one):
echo    Option A - Using IntelliJ IDEA (Recommended):
echo      - Open backend project in IDEA
echo      - Run LogisticsApplication.java
echo.
echo    Option B - Using Maven (if installed):
echo      - cd backend
echo      - mvn spring-boot:run
echo.
echo 2. Start Frontend:
echo    - cd frontend
echo    - npm run dev
echo.
echo 3. Access:
echo    - Frontend: http://localhost:5173
echo    - Backend:  http://localhost:8080
echo.
echo ===================================================================
echo.
pause
