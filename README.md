# 🧠 智能物流需求概率预测与决策系统

**Smart Logistics Demand Probabilistic Forecasting & Decision System**

---

## 📌 项目简介

面向物流弹性决策的深度学习系统，融合**图变分自编码器**与**条件标准化流**，实现时变概率需求预测与不确定性量化。系统以SaaS形态交付，适配大屏看板与移动巡检双场景。

### 核心功能
- 🔮 **概率需求预测**：未来7天包裹量分布预测（中位数 + 分位数区间）
- ⚠️ **智能预警**：自动对比网点处理能力，红色预警超载风险
- 🗺️ **空间依赖热力图**：GNNExplainer追溯上游网点影响
- 📊 **决策仪表盘**：全网实时概览 + 决策成本对比
- 📱 **PWA跨平台**：电脑端 + 手机端，一键安装到主屏幕

### 技术栈
| 层级 | 技术 |
|------|------|
| 前端 | Vue 3.4+, Vant 4.9+, Element Plus 2.7+, ECharts 5.5+, Leaflet 1.9.4, Vite 5.4+ |
| 后端 | Spring Boot 3.2.5, Spring Security 6.2+, MyBatis Plus 3.5.5, DJL 0.24.0 |
| 数据库 | MySQL 8.0, Redis 7.2 |
| 科研 | PyTorch 2.2+, PyTorch Geometric 2.5+, Matplotlib, Jupyter |
| 部署 | Docker 24+, Nginx 1.25+, Docker Compose 2.24+ |

---

## 🚀 本地运行指南

### 环境要求
- JDK 17
- Node.js 18+
- MySQL 8.0
- Redis 7.2
- Python 3.10+ (科研部分)
- Docker & Docker Compose (部署)

### 快速启动

```bash
# 1. 克隆仓库
git clone <repo-url>
cd Ghr_Science

# 2. 启动基础设施
docker-compose -f docker/docker-compose.yml up -d mysql redis

# 3. 后端
cd backend
./mvnw spring-boot:run

# 4. 前端
cd frontend
npm install
npm run dev

# 5. 访问
# 电脑端: http://localhost:5173
# 手机端: http://<your-ip>:5173
```

### 一键部署

```bash
docker-compose -f docker/docker-compose.yml up -d
```

---

## 📂 项目结构

```
Ghr_Science/
├── frontend/          # Vue3 PWA 前端
├── backend/           # Spring Boot 后端
├── research/          # PyTorch 科研代码
├── docker/            # Docker 部署配置
├── docs/              # 项目文档
└── README.md
```

---

## 📖 相关文档

- [API接口文档](docs/api.md)
- [部署说明](docs/deployment.md)
- [科研论文](docs/paper.md)

---

## 📊 系统截图

<!-- TODO: 添加系统截图 -->
| 功能 | 截图 |
|------|------|
| 决策仪表盘 | ![仪表盘](docs/screenshots/dashboard.png) |
| 预测瀑布图 | ![预测](docs/screenshots/forecast.png) |
| 手机端 | ![手机端](docs/screenshots/mobile.png) |

---

## 🔗 相关链接

- 论文题目：《面向物流弹性决策的时变概率需求预测：动态图变分流与不确定性校准》
- 目标期刊：Applied Soft Computing (IF 8.7, 中科院二区)
- 数据集：NYC TLC Trip Record Data (2010-2022)

---

## 📄 License

MIT License
