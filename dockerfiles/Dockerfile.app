FROM python:3.9-slim-bullseye
LABEL maintainer='alexsfa'

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8051

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        streamlit-user
        
ENV PATH="/py/bin:$PATH"

USER streamlit-user

CMD ["streamlit", "run", "main.py", "--server.port=8051"]
