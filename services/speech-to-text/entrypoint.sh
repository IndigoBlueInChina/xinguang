#!/bin/sh
set -e

# Ensure the app user can write to the mounted volumes and home directory.
# This script runs as root before the main application starts.
chown -R appuser:appuser /app/models /app/uploads /app/logs /home/appuser
chmod -R 755 /home/appuser

# Execute the main command (CMD) as the non-root user 'appuser'.
exec gosu appuser "$@"