#!/bin/sh
set -e

python -m app.utils.seed_admin
exec uvicorn app.main:app --host 0.0.0.0 --port 1111
