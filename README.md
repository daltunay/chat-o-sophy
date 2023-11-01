# chat-o-sophy

## Prerequisites

Poetry: If Poetry is not installed, you can do so using pip:


```bash
pip install poetry
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/chat-o-sophy.git
cd chat-o-sophy
```

2. Set up the project dependencies using Poetry:

```bash
poetry install
```

This command will create a virtual environment and install the necessary dependencies.

## (Optional) Setting up a default OpenAI API Key

The application lets the user decide whether to use their own API key or the default one.  
You can specifiy the default key in `.streamlit/secrets.toml`: 

```toml
[openai_api]
key="sk-..."
```

## Running the Application
The _chat-o-sophy_ application can be run using either Poetry or Docker.

### Using Poetry

To run the application using Poetry:

```bash
poetry run streamlit run Home.py
```

### Using Docker

1. Build the Docker image:

```bash
docker build -t chat-o-sophy .
```

2. Run the application as a Docker container:

```bash
docker run -p 8501:8501 chat-o-sophy
```

Once the application is running, it will be accessible at http://localhost:8501 in your web browser.
