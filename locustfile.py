"""
Locust Load Testing Configuration

Run with: locust -f locustfile.py --host=http://localhost:5000
Web UI: http://localhost:8089
"""

from locust import HttpUser, task, between, TaskSet
import random
import json


class ServiceManagementTasks(TaskSet):
    """Tasks for service management operations"""

    def on_start(self):
        """Setup - runs once when user starts"""
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data.get('token')
        else:
            self.token = None

    @task(10)
    def list_services(self):
        """List all services (most common operation)"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.client.get("/api/v1/services", headers=headers)

    @task(5)
    def get_service_details(self):
        """Get details of a specific service"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        # Random service ID between 1-100
        service_id = random.randint(1, 100)
        self.client.get(f"/api/v1/services/{service_id}", headers=headers)

    @task(3)
    def search_services(self):
        """Search services"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        search_terms = ["Shopping", "Cleaning", "Transport", "Cooking", "Bavaria"]
        term = random.choice(search_terms)

        self.client.get(f"/api/v1/services?search={term}", headers=headers)

    @task(2)
    def create_service(self):
        """Create a new service"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        service_data = {
            "service_name": f"Load Test Service {random.randint(1, 10000)}",
            "region": random.choice(["Bavaria", "Berlin", "Hamburg", "Saxony"]),
            "brutto_rate": round(random.uniform(30.0, 60.0), 2),
            "hours_per_month": random.choice([80, 120, 160, 200])
        }

        self.client.post("/api/v1/services", json=service_data, headers=headers)

    @task(1)
    def update_service(self):
        """Update an existing service"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        service_id = random.randint(1, 100)
        update_data = {
            "brutto_rate": round(random.uniform(30.0, 60.0), 2),
            "hours_per_month": random.choice([80, 120, 160, 200])
        }

        self.client.put(f"/api/v1/services/{service_id}", json=update_data, headers=headers)


class CalculatorTasks(TaskSet):
    """Tasks for financial calculator"""

    @task
    def calculate_rate(self):
        """Calculate hourly rate"""
        calc_data = {
            "brutto_rate": round(random.uniform(30.0, 60.0), 2),
            "hours_per_month": random.choice([80, 120, 160, 200]),
            "region": random.choice(["Bavaria", "Berlin", "Hamburg", "Saxony"]),
            "use_umlages": random.choice([True, False])
        }

        self.client.post("/api/v1/calculate", json=calc_data)


class StatisticsTasks(TaskSet):
    """Tasks for statistics and analytics"""

    @task(5)
    def get_statistics(self):
        """Get system statistics"""
        headers = {}
        self.client.get("/api/v1/statistics", headers=headers)

    @task(2)
    def get_regional_stats(self):
        """Get regional statistics"""
        region = random.choice(["Bavaria", "Berlin", "Hamburg", "Saxony"])
        self.client.get(f"/api/v1/statistics/region/{region}")


class WebUITasks(TaskSet):
    """Tasks for web UI endpoints"""

    @task(10)
    def home_page(self):
        """Visit home page"""
        self.client.get("/")

    @task(5)
    def dashboard(self):
        """Visit dashboard"""
        self.client.get("/dashboard")

    @task(3)
    def services_list(self):
        """Visit services list page"""
        self.client.get("/services")

    @task(2)
    def calculator_page(self):
        """Visit calculator page"""
        self.client.get("/calculator")

    @task(1)
    def analytics_page(self):
        """Visit analytics page"""
        self.client.get("/analytics")


class APIUser(HttpUser):
    """API user behavior - focuses on API endpoints"""
    tasks = [ServiceManagementTasks, CalculatorTasks, StatisticsTasks]
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    weight = 3  # 3x more likely than WebUser


class WebUser(HttpUser):
    """Web UI user behavior - focuses on page loads"""
    tasks = [WebUITasks]
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    weight = 1


class MixedUser(HttpUser):
    """Mixed user behavior - uses both API and Web UI"""
    tasks = [ServiceManagementTasks, WebUITasks, CalculatorTasks]
    wait_time = between(1, 4)
    weight = 2


# Custom load shapes
from locust import LoadTestShape

class StepLoadShape(LoadTestShape):
    """
    A step load shape that gradually increases load

    Usage: locust -f locustfile.py --host=http://localhost:5000 --headless --users 100 --spawn-rate 10
    """

    step_time = 30  # Seconds per step
    step_load = 10   # Users per step
    spawn_rate = 2   # Users to spawn per second
    time_limit = 600  # Total test time (10 minutes)

    def tick(self):
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        current_step = int(run_time // self.step_time)
        return (current_step + 1) * self.step_load, self.spawn_rate


class SpikesLoadShape(LoadTestShape):
    """
    A load shape that simulates traffic spikes

    Alternates between low and high load
    """

    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 5},   # 1 min baseline
        {"duration": 120, "users": 100, "spawn_rate": 20}, # 2 min spike
        {"duration": 180, "users": 10, "spawn_rate": 5},   # 3 min cooldown
        {"duration": 240, "users": 200, "spawn_rate": 50}, # 4 min big spike
        {"duration": 300, "users": 10, "spawn_rate": 5},   # 5 min cooldown
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None


# Event hooks for custom metrics
from locust import events

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Executed once when test starts"""
    print("=" * 60)
    print("DMS Load Test Starting")
    print(f"Host: {environment.host}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Executed once when test stops"""
    print("=" * 60)
    print("DMS Load Test Complete")
    print("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Log slow requests"""
    if response_time > 2000:  # Log requests slower than 2 seconds
        print(f"SLOW REQUEST: {request_type} {name} took {response_time}ms")


# Custom success/failure criteria
@events.quitting.add_listener
def check_success_criteria(environment, **kwargs):
    """Check if test passed success criteria"""
    stats = environment.stats.total

    # Success criteria:
    # - Less than 1% failure rate
    # - Average response time under 500ms
    # - 95th percentile under 1000ms

    fail_ratio = stats.fail_ratio
    avg_response_time = stats.avg_response_time
    percentile_95 = stats.get_response_time_percentile(0.95)

    success = True

    if fail_ratio > 0.01:
        print(f"FAIL: Failure rate {fail_ratio*100:.2f}% exceeds 1%")
        success = False

    if avg_response_time > 500:
        print(f"WARN: Average response time {avg_response_time:.0f}ms exceeds 500ms")

    if percentile_95 > 1000:
        print(f"WARN: 95th percentile {percentile_95:.0f}ms exceeds 1000ms")

    if success:
        print("SUCCESS: All performance criteria met")

    environment.process_exit_code = 0 if success else 1
