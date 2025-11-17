#!/bin/sh
python3 exec_db.py
python3 poblar_sincro.py
exec "$@"
