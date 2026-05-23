#!/bin/sh
set -e


echo "Waiting for Babelfish..."
while ! python -c "import pymssql; pymssql.connect(server='localhost', port=1433, user='babelfish_user', password='12345678').close()" 2>/dev/null; do
    sleep 2
done
echo "Babelfish ready."

python -m pyftpdlib -D --port 21 -w -d /app/app/static/scraped &

flask init-db

exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 'app:app'
