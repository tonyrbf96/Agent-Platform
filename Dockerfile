FROM python:3.7-slim
RUN mkdir -p /app
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
CMD ["python", "client.py"]