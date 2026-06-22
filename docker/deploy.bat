@echo off
echo =========================================
echo Logistics System - Deploy Script
echo =========================================

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker not installed
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Docker Compose not installed
    pause
    exit /b 1
)

echo [OK] Docker environment check passed

cd /d "%~dp0"

echo [STEP 1] Stopping old containers...
docker-compose down

set /p clean="Clean old images? (y/n): "
if /i "%clean%"=="y" (
    echo [STEP 2] Cleaning old images...
    docker-compose down --rmi all
)

echo [STEP 3] Building images and starting containers...
docker-compose up -d --build

echo [STEP 4] Waiting for services to start...
timeout /t 10 /nobreak >nul

echo [STEP 5] Container status:
docker-compose ps

echo.
echo =========================================
echo Deployment Complete!
echo =========================================
echo Access URLs:
echo   Frontend: http://localhost
echo   Backend:  http://localhost:8080
echo   API Docs: http://localhost:8080/swagger-ui/index.html
echo.
echo Default Admin Account:
echo   Username: admin
echo   Password: admin123
echo.
echo View Logs:
echo   docker-compose logs -f backend
echo   docker-compose logs -f frontend
echo.
echo Stop Services:
echo   docker-compose down
echo =========================================
pause