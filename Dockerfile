FROM python:3.11-slim

ENV BOT_TOKEN=${BOT_TOKEN}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
