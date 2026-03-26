# /opt/takk/gunicorn.conf.py
# Gunicorn configuration for TAKK production deployment

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker configuration
# Formula: (2 x CPU cores) + 1
# 1 vCPU: (2 x 1) + 1 = 3
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Process naming
proc_name = "takk"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "/var/log/takk/access.log"
errorlog = "/var/log/takk/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


# Process naming
def on_starting(server):
    server.log.info("Starting TAKK application")


def on_reload(server):
    server.log.info("Reloading TAKK application")


def when_ready(server):
    server.log.info("TAKK is ready to accept connections")


def on_exit(server):
    server.log.info("Shutting down TAKK application")
