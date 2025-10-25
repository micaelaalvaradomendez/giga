FROM python:3.11-slim


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

WORKDIR /app


RUN python -m venv /venv \
    && pip install --upgrade pip


COPY back/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt


COPY back/ /app/


RUN mkdir -p /app/logs /app/staticfiles /app/media


COPY back/docker/entrypoint.sh /entrypoint.sh
COPY back/docker/init_db.sh /init_db.sh
COPY back/docker/wait_for_db.py /wait_for_db.py

# blindaje contra CRLF (problema Windows)
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
RUN sed -i 's/\r$//' /init_db.sh && chmod +x /init_db.sh

EXPOSE 8000

CMD ["/init_db.sh"]

