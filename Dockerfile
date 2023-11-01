# Use Python 3.11 slim Buster as the base image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy dependency files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry and project dependencies
RUN pip install "poetry==1.4.2" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root --no-interaction

# Copy the rest of the application files
COPY . /app

# Expose port 8501 (Streamlit default port)
EXPOSE 8501

# Define the command to run the Streamlit application
CMD ["streamlit", "run", "Home.py"]
