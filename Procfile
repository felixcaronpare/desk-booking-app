web: gunicorn booking.wsgi --log-file -
release: python manage.py migrate && python manage.py setup_desks
