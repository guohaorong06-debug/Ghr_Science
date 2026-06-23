#!/bin/bash

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║      🚀 智能物流系统 - 本地启动（推荐方案）🚀               ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 检查Docker
echo "[1/6] 检查Docker环境..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi
echo "✅ Docker运行正常"
echo ""

# 启动MySQL和Redis
echo "[2/6] 启动数据库服务（MySQL + Redis）..."
cd docker
docker compose up -d mysql redis
if [ $? -ne 0 ]; then
    echo "❌ 数据库启动失败"
    exit 1
fi
echo "✅ 数据库服务已启动"
echo ""

# 等待数据库就绪
echo "[3/6] 等待数据库就绪（30秒）..."
sleep 30
echo "✅ 数据库就绪"
echo ""

# 检查Maven
echo "[4/6] 检查后端环境..."
if ! command -v mvn &> /dev/null; then
    echo "⚠️ 未检测到Maven"
    echo "   请使用IntelliJ IDEA运行LogisticsApplication"
    exit 1
fi
echo "✅ Maven已安装"
echo ""

# 启动后端
echo "[5/6] 启动后端服务..."
cd ../backend
gnome-terminal -- bash -c "echo '🚀 后端启动中...' && mvn clean spring-boot:run; exec bash" &
echo "✅ 后端正在启动（新终端）"
sleep 20
echo ""

# 启动前端
echo "[6/6] 启动前端服务..."
cd ../frontend
gnome-terminal -- bash -c "echo '🚀 前端启动中...' && npm run dev; exec bash" &
echo "✅ 前端正在启动（新终端）"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎊 系统启动完成！"
echo ""
echo "📋 访问地址:"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8080"
echo "   Swagger: http://localhost:8080/swagger-ui/index.html"
echo ""
echo "📋 测试账号:"
echo "   管理员: admin / 123456"
echo "   运营员: operator / 123456"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
