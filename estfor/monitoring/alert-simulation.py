#!/usr/bin/env python3
"""
Alert Simulation Script for EstFor Monitoring System
This script simulates various alert conditions for testing the monitoring setup.
"""

import requests
import time
import random
import threading
from datetime import datetime

# Configuration
APP_URL = "http://localhost:8000"
SIMULATION_DURATION = 300  # 5 minutes
ERROR_RATE = 0.3  # 30% error rate during simulation

def log_message(message):
    """Log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def simulate_high_error_rate():
    """Simulate high error rate by making requests to non-existent endpoints"""
    log_message("🚨 Starting high error rate simulation...")
    
    start_time = time.time()
    while time.time() - start_time < SIMULATION_DURATION:
        try:
            # Make requests to non-existent endpoints to generate 404s
            if random.random() < ERROR_RATE:
                response = requests.get(f"{APP_URL}/non-existent-endpoint", timeout=5)
                log_message(f"Generated 404 error: {response.status_code}")
            else:
                # Make normal requests to health endpoint
                response = requests.get(f"{APP_URL}/health", timeout=5)
                log_message(f"Normal request: {response.status_code}")
            
            time.sleep(2)  # Wait 2 seconds between requests
            
        except requests.exceptions.RequestException as e:
            log_message(f"Request error: {e}")
            time.sleep(1)
    
    log_message("✅ High error rate simulation completed")

def simulate_high_response_time():
    """Simulate high response time by making slow requests"""
    log_message("🐌 Starting high response time simulation...")
    
    start_time = time.time()
    while time.time() - start_time < SIMULATION_DURATION:
        try:
            # Add artificial delay to simulate slow responses
            time.sleep(random.uniform(1, 3))
            response = requests.get(f"{APP_URL}/health", timeout=10)
            log_message(f"Slow request completed: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            log_message(f"Request error: {e}")
            time.sleep(1)
    
    log_message("✅ High response time simulation completed")

def simulate_service_unavailability():
    """Simulate service unavailability by stopping the app temporarily"""
    log_message("⚠️  Service unavailability simulation - this will stop the app for 30 seconds")
    log_message("   Run this in a separate terminal after starting the simulation:")
    log_message("   docker-compose stop app")
    log_message("   # Wait 30 seconds")
    log_message("   docker-compose start app")

def check_monitoring_endpoints():
    """Check if monitoring endpoints are accessible"""
    endpoints = {
        "Prometheus": "http://localhost:9090",
        "Grafana": "http://localhost:3000",
        "AlertManager": "http://localhost:9093",
        "cAdvisor": "http://localhost:8082"
    }
    
    log_message("🔍 Checking monitoring endpoints...")
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url, timeout=5)
            log_message(f"✅ {name}: {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            log_message(f"❌ {name}: {url} - Error: {e}")

def main():
    """Main function to run alert simulations"""
    log_message("🚀 EstFor Alert Simulation Started")
    log_message("=" * 50)
    
    # Check monitoring endpoints first
    check_monitoring_endpoints()
    log_message("")
    
    # Run simulations
    print("Choose simulation type:")
    print("1. High Error Rate Simulation")
    print("2. High Response Time Simulation")
    print("3. Service Unavailability Instructions")
    print("4. Run All Simulations")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        simulate_high_error_rate()
    elif choice == "2":
        simulate_high_response_time()
    elif choice == "3":
        simulate_service_unavailability()
    elif choice == "4":
        # Run error rate simulation in background
        error_thread = threading.Thread(target=simulate_high_error_rate)
        error_thread.start()
        
        # Run response time simulation in background
        response_thread = threading.Thread(target=simulate_high_response_time)
        response_thread.start()
        
        # Wait for both to complete
        error_thread.join()
        response_thread.join()
    else:
        log_message("❌ Invalid choice")
        return
    
    log_message("")
    log_message("📊 Check your monitoring dashboards:")
    log_message("   - Grafana: http://localhost:3000 (admin/admin)")
    log_message("   - AlertManager: http://localhost:9093")
    log_message("   - Prometheus: http://localhost:9090")
    log_message("")
    log_message("🎯 Look for alerts in the 'EstFor Alert Monitoring' dashboard")

if __name__ == "__main__":
    main() 