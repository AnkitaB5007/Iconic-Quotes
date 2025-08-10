FROM python:3.9-slim

ARG APP_VERSION=1.0
RUN echo "Building Flask app : version $APP_VERSION"
ENV APP_PORT=5000

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE $APP_PORT

CMD ["python", "app.py"]