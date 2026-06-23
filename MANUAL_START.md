# Manual Startup Guide

Due to encoding issues with .bat files, please follow these manual steps:

## Step 1: Start Database

Open CMD window and run:
```cmd
cd D:\Ghr_Science\docker
docker compose up -d mysql redis
```

Wait 30 seconds for initialization.

## Step 2: Start Backend (Using IntelliJ IDEA)

1. Open IntelliJ IDEA
2. Open project: `D:\Ghr_Science\backend`
3. Find file: `src/main/java/com/logistics/LogisticsApplication.java`
4. Right-click → Run 'LogisticsApplication'
5. Wait for console to show: "Started LogisticsApplication"

## Step 3: Start Frontend

Open another CMD window and run:
```cmd
cd D:\Ghr_Science\frontend
npm run dev
```

## Access

- Frontend: http://localhost:5173
- Backend: http://localhost:8080
- Swagger: http://localhost:8080/swagger-ui/index.html

## Test Accounts

- Admin: `admin` / `123456`
- Operator: `operator` / `123456`
- Guest: `guest` / `123456`

## Stop Services

- Backend: Click Stop button in IDEA
- Frontend: Press Ctrl+C in CMD window
- Database: `docker compose down`

---

This is the most reliable method!
