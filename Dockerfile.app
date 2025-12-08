FROM python:3.9-slim-bullseye
LABEL maintainer='alexsfa'

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8051

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    adduser --disabled-password --gecos "" --home /home/streamlit-user streamlit-user && \
    mkdir -p /home/streamlit-user/.streamlit && \
    cp /app/.streamlit/config.toml /home/streamlit-user/.streamlit/config.toml && \
    chown -R streamlit-user:streamlit-user /home/streamlit-user/.streamlit && \
    chown -R streamlit-user:streamlit-user /app
        
ENV PATH="/py/bin:$PATH"
ENV HOME="/home/streamlit-user"

USER streamlit-user

CMD ["python","./utils/watch_script.py"]
