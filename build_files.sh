#!/bin/bash
# Vercel build script — runs during deployment to collect static files.
# Vercel executes this automatically because it is referenced in vercel.json.

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Build complete."
