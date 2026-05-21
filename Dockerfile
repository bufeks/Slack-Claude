FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py slack_client.py unreplied_mentions.py bot.py ./

CMD ["python", "bot.py"]
