#!/bin/sh
set -e

# Ensure the app user can write to the mounted volumes.
# This script runs as root before the main application starts.
chown -R appuser:appuser /app/models /app/uploads /app/logs

# Execute the main command (CMD) as the non-root user 'appuser'.
exec gosu appuser "$@"