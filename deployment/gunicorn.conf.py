# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/algoritmika/access.log'
errorlog = '/var/log/algoritmika/error.log'
loglevel = 'debug'  # Временно включаем debug для диагностики
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = 'gunicorn_algoritmika'

# User and group
user = 'algoritmika'
group = 'algoritmika'

# SSL Configuration (если потребуется)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'