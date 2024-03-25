FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY autotrade.py .
COPY .env .
COPY instructions.md .

CMD ["python", "./coinstrategy/autotrade.py"]
