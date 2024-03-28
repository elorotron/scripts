#!/bin/bash

# check free disk space percentage
check_free_space() {
    free_space=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    echo "Current free disk space: $free_space%"
}

# clear Docker cache
clear_cache() {
    echo "Clearing Docker cache..."
    docker system prune -a -f
    echo "Docker cache cleared."
}

# Main script
check_free_space

# Set a threshold for free disk space percentage
threshold_percentage="80"

if [ "$free_space" -gt "$threshold_percentage" ]; then
    echo "Free disk space exceeds the threshold. Clearing Docker cache..."
    clear_cache
else
    echo "Free disk space is within the threshold. No action needed."
fi

# crontab -e
# 0 * * * * /home/ubuntu/bash_script/clear_docker_cache.sh