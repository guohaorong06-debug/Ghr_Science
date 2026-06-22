"""
API接口自动化测试

测试所有后端API接口的功能和性能
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8080/api"
RESULTS_DIR = Path("../tests/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.test_user_id = None
        self.test_site_id = None

    def log_test(self, module, test_name, success, response_time, details):
        """记录测试结果"""
        result = {
            "module": module,
            "test_name": test_name,
            "success": success,
            "response_time_ms": round(response_time * 1000, 2),
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} [{module}] {test_name} ({result['response_time_ms']}ms)")
        if not success:
            print(f"   Error: {details}")

    def test_register(self):
        """测试用户注册"""
        url = f"{BASE_URL}/auth/register"
        payload = {
            "username": f"test_user_{int(time.time())}",
            "password": "Test123456",
            "realName": "测试用户",
            "email": "test@example.com"
        }

        start = time.time()
        try:
            response = self.session.post(url, json=payload)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                self.log_test("Auth", "用户注册", data.get("code") == 200, elapsed, data.get("message"))
                return True
            else:
                self.log_test("Auth", "用户注册", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth", "用户注册", False, 0, str(e))
            return False

    def test_login(self):
        """测试用户登录"""
        url = f"{BASE_URL}/auth/login"
        payload = {
            "username": "admin",
            "password": "admin123"
        }

        start = time.time()
        try:
            response = self.session.post(url, json=payload)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    self.token = data["data"]["token"]
                    self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                    self.log_test("Auth", "用户登录", True, elapsed, f"Token获取成功")
                    return True
                else:
                    self.log_test("Auth", "用户登录", False, elapsed, data.get("message"))
                    return False
            else:
                self.log_test("Auth", "用户登录", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth", "用户登录", False, 0, str(e))
            return False

    def test_get_user_info(self):
        """测试获取用户信息"""
        url = f"{BASE_URL}/auth/info"

        start = time.time()
        try:
            response = self.session.get(url)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                success = data.get("code") == 200 and "username" in data.get("data", {})
                self.log_test("Auth", "获取用户信息", success, elapsed,
                             f"用户: {data.get('data', {}).get('username')}")
                return success
            else:
                self.log_test("Auth", "获取用户信息", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Auth", "获取用户信息", False, 0, str(e))
            return False

    def test_create_site(self):
        """测试创建网点"""
        url = f"{BASE_URL}/site"
        payload = {
            "name": f"测试网点_{int(time.time())}",
            "longitude": -73.98,
            "latitude": 40.75,
            "gridId": 25,
            "capacity": 1000,
            "description": "自动化测试创建"
        }

        start = time.time()
        try:
            response = self.session.post(url, json=payload)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                success = data.get("code") == 200
                self.log_test("Site", "创建网点", success, elapsed, data.get("message"))
                return success
            else:
                self.log_test("Site", "创建网点", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Site", "创建网点", False, 0, str(e))
            return False

    def test_list_sites(self):
        """测试查询网点列表"""
        url = f"{BASE_URL}/site/list"

        start = time.time()
        try:
            response = self.session.get(url)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                sites = data.get("data", [])
                success = data.get("code") == 200
                if sites and len(sites) > 0:
                    self.test_site_id = sites[0].get("id")
                self.log_test("Site", "查询网点列表", success, elapsed,
                             f"共{len(sites)}个网点")
                return success
            else:
                self.log_test("Site", "查询网点列表", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Site", "查询网点列表", False, 0, str(e))
            return False

    def test_forecast(self):
        """测试预测功能"""
        if not self.test_site_id:
            self.log_test("Forecast", "预测服务", False, 0, "未找到测试网点ID")
            return False

        url = f"{BASE_URL}/forecast/predict"
        payload = {
            "siteId": self.test_site_id,
            "startDate": "2024-01-01",
            "conditions": {
                "weather": "sunny",
                "promotion": False
            }
        }

        start = time.time()
        try:
            response = self.session.post(url, json=payload)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                results = data.get("data", [])
                success = data.get("code") == 200 and len(results) == 7
                self.log_test("Forecast", "预测服务", success, elapsed,
                             f"生成{len(results)}天预测")
                return success
            else:
                self.log_test("Forecast", "预测服务", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Forecast", "预测服务", False, 0, str(e))
            return False

    def test_get_alerts(self):
        """测试查询预警"""
        url = f"{BASE_URL}/forecast/alerts"

        start = time.time()
        try:
            response = self.session.get(url)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                alerts = data.get("data", [])
                success = data.get("code") == 200
                self.log_test("Forecast", "查询预警", success, elapsed,
                             f"共{len(alerts)}条预警")
                return success
            else:
                self.log_test("Forecast", "查询预警", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Forecast", "查询预警", False, 0, str(e))
            return False

    def test_list_models(self):
        """测试查询模型列表"""
        url = f"{BASE_URL}/model/list"

        start = time.time()
        try:
            response = self.session.get(url)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                success = data.get("code") == 200
                self.log_test("Model", "查询模型列表", success, elapsed,
                             f"共{len(models)}个模型")
                return success
            else:
                self.log_test("Model", "查询模型列表", False, elapsed, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Model", "查询模型列表", False, 0, str(e))
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("API接口自动化测试")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标服务: {BASE_URL}")
        print("=" * 80)

        # 运行测试
        tests = [
            self.test_register,
            self.test_login,
            self.test_get_user_info,
            self.test_create_site,
            self.test_list_sites,
            self.test_forecast,
            self.test_get_alerts,
            self.test_list_models,
        ]

        for test in tests:
            test()
            time.sleep(0.5)  # 避免请求过快

        # 统计结果
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        avg_time = sum(r["response_time_ms"] for r in self.test_results) / total if total > 0 else 0

        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"总测试数: {total}")
        print(f"通过: {passed} ({passed/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        print(f"平均响应时间: {avg_time:.2f}ms")
        print("=" * 80)

        # 保存结果
        report = {
            "test_suite": "API接口测试",
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": round(passed/total*100, 2) if total > 0 else 0,
                "average_response_time_ms": round(avg_time, 2)
            },
            "details": self.test_results
        }

        output_file = RESULTS_DIR / "api_test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n详细结果已保存: {output_file}")

        return passed == total

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
