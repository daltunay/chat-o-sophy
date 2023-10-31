## How to Run

To run the application, follow these steps:

### Step 1: Build the Docker Image

Execute the following command to build the Docker image:

```bash
docker build -t chat-o-sophy .
```

### Step 2: Run the Application

Once the image is built, run the application using the command:

```bash
docker run -p 8501:8501 chat-o-sophy
```

This will start the _chat-o-sophy_ application and make it accessible locally at http://localhost:8501.