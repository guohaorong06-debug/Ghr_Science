# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Smart Logistics Demand Probabilistic Forecasting & Decision System** — A full-stack SaaS platform combining deep learning research (GraphVAE + Normalizing Flow) with production-ready web application for logistics demand prediction and decision support.

**Tech Stack**:
- Frontend: Vue 3.4 + Vant 4.9 (mobile) + Element Plus 2.7 (desktop) + ECharts 5.5 + Leaflet
- Backend: Spring Boot 3.2.5 + Spring Security 6.2 + MyBatis-Plus 3.5.5 + DJL 0.24.0 (PyTorch inference)
- Database: MySQL 8.0 + Redis 7.2
- Research: PyTorch 2.2 + PyTorch Geometric 2.5
- Deployment: Docker + Docker Compose

---

## Development Commands

### Backend (Spring Boot)

```bash
cd backend

# Run in development mode (IDEA recommended)
# Open LogisticsApplication.java → Right-click → Run

# Or via Maven
./mvnw spring-boot:run

# Build
./mvnw clean package -DskipTests

# Test
./mvnw test
```

**Backend starts on**: http://localhost:8080  
**Swagger API**: http://localhost:8080/swagger-ui/index.html

### Frontend (Vue 3 + Vite)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Format code
npm run format
```

**Frontend runs on**: http://localhost:5173

### Database (Docker)

```bash
cd docker

# Start MySQL + Redis only (for local development)
docker compose up -d mysql redis

# Check status
docker ps

# Stop services
docker compose down

# View logs
docker compose logs -f mysql
```

**MySQL**: localhost:3306, user: `root`, password: `logistics2026`, database: `logistics`  
**Redis**: localhost:6379

### Research (PyTorch)

```bash
cd research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train models
python train_lstm.py
python train_gru.py
python train_transformer.py
python train_graphvae.py

# Export to TorchScript (for Java inference)
python export_torchscript.py
```

Trained models are exported to `models/*.pt` for backend inference.

### Full System (Docker Compose)

```bash
cd docker

# Start all services (MySQL + Redis + Backend + Frontend)
docker compose up -d

# Stop all
docker compose down

# View logs
docker compose logs -f backend
```

**Access**: http://localhost (Nginx serves frontend, proxies `/api` to backend)

---

## Architecture Overview

### Three-Tier Structure

```
research/          → Model training (Python/PyTorch)
    ├── models/    → Trained .pt files (TorchScript format)
    └── data/      → NYC TLC dataset (not in repo, see research/DATA_DOWNLOAD_OPTIONS.md)

backend/           → Spring Boot API server
    ├── controller/    → REST endpoints (/api/*)
    ├── service/       → Business logic + model inference (DJL)
    ├── mapper/        → MyBatis-Plus DB access
    ├── entity/        → JPA entities
    └── security/      → JWT + Spring Security config

frontend/          → Vue 3 PWA (responsive desktop + mobile)
    ├── views/         → Page components
    ├── components/    → Reusable UI components
    ├── api/           → Axios API calls
    └── stores/        → Pinia state management
```

### Key Patterns

**Backend — Model Loading (Lazy Initialization)**:
- `ModelLoaderService` uses lazy loading to avoid blocking startup
- Models are loaded on first prediction request via `ensureInitialized()`
- PyTorch native libraries are downloaded automatically by DJL (CPU mode)

**Backend — RBAC Permissions**:
- Three roles: `ADMIN`, `OPERATOR`, `GUEST`
- Permissions stored in `sys_permission` table
- Role-permission mapping in `sys_role_permission`
- Enforced via Spring Security + `@PreAuthorize` annotations

**Frontend — Responsive Design**:
- Desktop: Element Plus (Navbar + Sidebar layout)
- Mobile: Vant (Tabbar navigation)
- Shared: Axios API client (`frontend/src/api/*.js`)
- PWA: Installable on mobile home screen (manifest + service worker)

**Database — Schema**:
- `sys_user`, `sys_role`, `sys_permission` → RBAC system
- `logistics_site` → Warehouse/distribution center data
- `logistics_data` → Historical demand records (14-day windows for prediction)
- `prediction_result` → Cached prediction outputs

**Research — Model Pipeline**:
1. Train in Python (`research/*.py`)
2. Export to TorchScript (`export_torchscript.py`)
3. Copy `.pt` files to `backend/models/` (or `docker/models/` for containers)
4. Backend loads via DJL `Model.load(Paths.get("models/lstm_torchscript.pt"))`

---

## Common Issues

### Backend won't start — "Failed to download PyTorch native library"
**Cause**: DJL tries to download PyTorch CPU libraries on first run (~150MB).  
**Fix**: Wait 1-2 minutes for download. Libraries are cached in `C:\Users\<user>\.djl.ai\pytorch\` (Windows) or `~/.djl.ai/pytorch/` (Linux/Mac). Subsequent starts are fast.

### Login fails — "Unknown column 'status' in field list"
**Cause**: Database schema missing `status` column in `sys_user` table.  
**Fix**: Run SQL patch:
```sql
ALTER TABLE sys_user ADD COLUMN status INT DEFAULT 1 AFTER role;
```
Or re-run `backend/src/main/resources/db/init.sql`.

### Frontend 404 on `/api/*` endpoints
**Cause**: Backend not running or not on port 8080.  
**Fix**: Check `backend/src/main/resources/application-dev.yml` has `server.port: 8080`. Ensure backend started successfully (look for "Started LogisticsApplication" in logs).

### CUDA version mismatch (GPU acceleration)
**Current config**: DJL 0.24.0 only supports CUDA 11.8, but system may have CUDA 12.3.  
**Workaround**: CPU mode is default and stable. GPU is not critical for demo/development. To enable GPU, see `GPU_SETUP.md` (requires CUDA 11.8 toolkit or DJL upgrade).

---

## Test Accounts

```
Admin:    admin    / 123456   (full access)
Operator: operator / 123456   (manage sites + data, no user management)
Guest:    guest    / 123456   (read-only)
```

---

## Documentation

- `MANUAL_START.md` — Step-by-step local startup guide
- `PROJECT_FINAL_REPORT.md` — Complete project summary
- `NEXT_STEPS.md` — Future improvements and production readiness checklist
- `paper/WRITING_GUIDE.md` — LaTeX paper structure for academic publication
- `research/TRAINING_GUIDE.md` — Model training instructions

---

## Notes

- **No .bat scripts**: Windows CMD has UTF-8 encoding issues. Use PowerShell or manual commands from MANUAL_START.md.
- **PyTorch in Java**: Backend uses DJL (Deep Java Library) to load TorchScript models. Models must be trained in Python first, then exported.
- **Mobile PWA**: Frontend uses Vant for mobile UI. Access from phone browser → "Add to Home Screen" for native-like experience.
- **Paper target**: Applied Soft Computing (IF 8.7, CAS Q1). See `paper/references.bib` for citation format.
