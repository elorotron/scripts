#!/usr/bin/env python3

import subprocess
import time
import boto3

# Variables
container_name = "fines-service-prod" # Container name to track
region_name = "your-region" # Region AWS

def check_container_status(container_name):
    try:
        output = subprocess.check_output(["docker", "inspect", "-f", "{{.State.Running}}", container_name])
        return output.strip() == b'true'
    except subprocess.CalledProcessError:
        return False

def get_cpu_usage():
    output = subprocess.check_output(["ps", "-eo", "pcpu", "--sort=-pcpu"])
    cpu_usage_lines = output.decode().split('\n')
    cpu_usage_lines = cpu_usage_lines[1:]
    total_cpu_usage = sum(float(line.strip()) for line in cpu_usage_lines if line.strip())
    return total_cpu_usage

def get_memory_usage():
    output = subprocess.check_output(["free", "-m"])
    lines = output.decode().split('\n')
    memory_line = lines[1]
    total_memory = int(memory_line.split()[1])
    used_memory = int(memory_line.split()[2])
    memory_usage = (used_memory / total_memory) * 100
    return memory_usage

def get_disk_usage():
    output = subprocess.check_output(["df", "-h"])
    lines = output.decode().split('\n')
    disk_line = lines[1]
    disk_usage = float(disk_line.split()[4].replace('%', ''))
    return disk_usage

def send_to_cloudwatch(metric_name, metric_value):
    cloudwatch = boto3.client("cloudwatch", region_name=region_name)

    cloudwatch.put_metric_data(
        Namespace="InstanceMetrics",
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": metric_value,
                "Unit": "Percent"
            }
        ]
    )

while True:
    container_running = check_container_status(container_name)
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()

    send_to_cloudwatch("ContainerStatus", 1 if container_running else 0)
    send_to_cloudwatch("CPUUsage", cpu_usage)
    send_to_cloudwatch("MemoryUsage", memory_usage)
    send_to_cloudwatch("DiskUsage", disk_usage)

    time.sleep(60)
