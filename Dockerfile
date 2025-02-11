FROM python:3.9-buster

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "lechbot.py", "--irc"]
