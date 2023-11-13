# chat-o-sophy

**Chat with your favorite philosophers!**

Access live deployed app here: **https://chat-o-sophy.streamlit.app/**

## Prerequisites

**Poetry**: If [Poetry](https://python-poetry.org/) is not installed, you can do so using pip:


```bash
pip install poetry
```

**Docker**: If [Docker](https://www.docker.com/) is not installed, you can do so following [this link](https://docs.docker.com/get-docker/)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/daltunay/chat-o-sophy.git
cd chat-o-sophy
```

2. Set up the project dependencies using Poetry:

```bash
poetry install
```

This command will create a virtual environment and install the necessary dependencies.

## (Optional) Setting up default API Keys

The application lets the user decide whether to use their own API keys or the default one.  
You can specifiy the default keys in `.streamlit/secrets.toml`: 

```toml
[openai_api]
key="<OPENAI_API_KEY>"

[replicate_api]
key="<REPLICATE_API_TOKEN>"

[lakera_guard_api]
key="<LAKERA_GUARD_API_KEY">
```

The default OpenAI key is used for the logo generation, as well as the `gpt-3.5-turbo` model if the default checkbox is ticked.  
The default Replicate key is used for the `llama-2-7b-chat` and `mistral-7b-instruct-v0.1` models if the default checkbox is ticked.

## Running the Application
The _chat-o-sophy_ application can be run using either Poetry or Docker.

### Using Poetry

To run the application using Poetry:

```bash
poetry run streamlit run ./src/Home.py
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

Alternatively, you can just run the following:

```bash
chmod +x ./bin/start.sh
./bin/start.sh
```

Once the application is running, it will be accessible at http://localhost:8501 in your web browser.
