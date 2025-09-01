#!/usr/bin/env bash
set -euo pipefail
cd /root/Vete1
source .venv/bin/activate
python manage.py collectstatic --noinput
python manage.py migrate
deactivate
sudo systemctl restart gunicorn
sudo systemctl reload nginx
echo "Deploy OK $(date)"
