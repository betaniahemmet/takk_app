# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"  # Nginx will proxy to this
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # For 6 cores: 13 workers
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/takk/access.log"
errorlog = "/var/log/takk/error.log"
loglevel = "info"

# Process naming
proc_name = "takk"

# Server mechanics
daemon = False  # Systemd handles daemonization
pidfile = "/var/run/takk/takk.pid"
user = "takk"
group = "takk"

# Preload app for better performance
preload_app = True

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
