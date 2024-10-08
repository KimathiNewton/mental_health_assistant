FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY dataset/data.csv dataset/data.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY src .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
