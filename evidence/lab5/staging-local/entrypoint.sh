#!/bin/sh
(cd /srv/app/src/alerts-api && python app.py) &
(cd /srv/app/src/actions-api && python app.py) &
exec nginx -g 'daemon off;'
