# alembic upgrade head
alembic -c app/alembic.ini upgrade head

exec "$@"