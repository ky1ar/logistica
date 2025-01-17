FROM python:3.11

WORKDIR /application
COPY . .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
