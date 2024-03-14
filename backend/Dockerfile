FROM python:3.8
WORKDIR /star-burger/
RUN mkdir -p /var/www/frontend/ \
	&& mkdir -p /var/www/media/ \
	&& mkdir -p /var/www/static/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ARG COMMIT_HASH
LABEL last_commit_hash="$COMMIT_HASH"
RUN python manage.py collectstatic --noinput
CMD ["sh", "-c", "./start_server.sh \"$COMMAND\""]
