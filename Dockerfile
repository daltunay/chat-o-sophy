FROM python:3.11-slim-buster

WORKDIR /app

COPY . /app

RUN pip install "poetry==1.7.0" \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-dev --no-cache

EXPOSE 8501

CMD ["streamlit", "run", "./src/chat_o_sophy/Home.py"]
