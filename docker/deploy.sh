#!/bin/bash

echo "========================================="
echo "智能物流决策系统 - 一键部署脚本"
echo "========================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 进入docker目录
cd "$(dirname "$0")"

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose down

# 清理旧镜像（可选）
read -p "是否清理旧镜像？(y/n): " clean
if [ "$clean" = "y" ]; then
    echo "🧹 清理旧镜像..."
    docker-compose down --rmi all
fi

# 构建并启动
echo "🔨 构建镜像并启动容器..."
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查容器状态
echo "📊 容器状态："
docker-compose ps

echo ""
echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo "访问地址："
echo "  前端：http://localhost"
echo "  后端：http://localhost:8080"
echo "  API文档：http://localhost:8080/swagger-ui/index.html"
echo ""
echo "默认管理员账号："
echo "  用户名：admin"
echo "  密码：admin123"
echo ""
echo "查看日志："
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend"
echo ""
echo "停止服务："
echo "  docker-compose down"
echo "========================================="
