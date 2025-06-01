# Deployment Guide for VirtualPackaging

This guide provides instructions for deploying the VirtualPackaging application using Docker and Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker:** Latest stable version. (See [Docker installation guide](https://docs.docker.com/engine/install/))
*   **Docker Compose:** Latest stable version. (Included with Docker Desktop for Mac and Windows. For Linux, see [Docker Compose installation guide](https://docs.docker.com/compose/install/))
*   **Git:** For cloning the repository.
*   **Python:** Version 3.8+ (for running any helper scripts, though not strictly required for Dockerized deployment).
*   **Node.js:** Version 18+ (if you need to build the frontend manually outside Docker).
*   **`.env` file:** You'll need a `.env` file in the project root, based on `.env.example` (if provided, or as per `setup_env.sh`). This file should contain necessary API keys (OpenAI, Anthropic, HuggingFace) and other configuration variables.

    Example content for `.env`:
    ```
    OPENAI_API_KEY=your_openai_key_here
    ANTHROPIC_API_KEY=your_anthropic_key_here
    HF_API_KEY=your_huggingface_key_here
    # Add other variables like WEB_HOST, WEB_PORT, DEBUG, etc., as needed.
    # Refer to web/config.py for backend configuration options.
    ```

## Deployment using Docker Compose

The easiest way to deploy VirtualPackaging is using the provided `docker-compose.yml` file. This will build and run the backend, frontend, and Nginx proxy.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/JJshome/VirtualPackaging.git
    cd VirtualPackaging
    ```

2.  **Create/Update `.env` file:**
    Ensure your `.env` file is present in the project root and correctly configured with your API keys and any other necessary settings.

3.  **Build and Run Containers:**
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker to rebuild the images. Use this for the first time or after code changes.
    *   `-d`: Runs containers in detached mode (in the background).

4.  **Accessing the Application:**
    Once the containers are up and running, the application should be accessible at `http://localhost:80` (or the port configured in Nginx/Docker Compose if different). The default Nginx configuration (`docker/nginx.conf`) routes:
    *   Requests to `/api` to the backend service.
    *   All other requests to the frontend service.

## Individual Component Deployment (Manual Steps)

### Backend Deployment

The backend is a FastAPI application.

*   **Dockerfile:** `docker/backend.Dockerfile`
*   **Steps (using Docker):**
    1.  Navigate to the project root.
    2.  Build the backend image:
        ```bash
        docker build -t virtualpackaging-backend -f docker/backend.Dockerfile .
        ```
    3.  Run the backend container:
        ```bash
        docker run -d --name vp-backend --env-file .env -p 8000:8000 virtualpackaging-backend
        ```
        (Ensure port 8000 is the one your FastAPI app listens on, as configured in `web/config.py` and the Dockerfile)

### Frontend Deployment

The frontend is a React application.

*   **Dockerfile:** `docker/frontend.Dockerfile`
*   **Steps (using Docker):**
    1.  Navigate to the project root.
    2.  Build the frontend image:
        ```bash
        docker build -t virtualpackaging-frontend -f docker/frontend.Dockerfile .
        ```
    3.  Run the frontend container (typically served by a static server like Nginx):
        ```bash
        docker run -d --name vp-frontend -p 3000:80 virtualpackaging-frontend
        ```
        (This example assumes the Docker image for the frontend serves content on port 80 internally. Adjust if your setup is different, e.g., if it's just building static files to be served by Nginx directly).

### Nginx Configuration

*   **Config File:** `docker/nginx.conf`
*   **Role:** Acts as a reverse proxy.
    *   Directs API traffic (e.g., `/api/*`) to the backend service.
    *   Serves the frontend static files for all other routes.
    *   Can handle SSL termination, load balancing (if scaled), and serving static assets efficiently.
*   When using `docker-compose.yml`, Nginx is automatically configured and run as part of the services.

## Production Considerations

*   **Database:** The current setup does not explicitly define a persistent database in Docker Compose. For production, you'll need to configure and link a persistent database (e.g., PostgreSQL, MongoDB as mentioned in `README.md`). This might involve adding a database service to `docker-compose.yml` and configuring the backend to connect to it.
*   **HTTPS:** For secure communication, configure Nginx to use SSL/TLS certificates (e.g., using Let's Encrypt).
*   **Scalability:** Depending on the load, you might need to scale services. Docker Compose allows scaling for stateless services. For more complex scaling, consider orchestration platforms like Kubernetes.
*   **Environment Variables:** Ensure all sensitive data (API keys, secrets) are managed securely, preferably through environment variables or a secrets management system, and NOT hardcoded. The `.env` file is suitable for development but might need a more robust solution for production.
*   **Logging & Monitoring:** Implement comprehensive logging and monitoring for all services.
*   **Data Persistence:** Ensure that any data generated by the application (e.g., uploaded files, design outputs if not stored in a database) is persisted using Docker volumes to prevent data loss when containers are stopped or restarted. Check `web/config.py` for `UPLOAD_DIR`.

## Stopping the Application

To stop the application when deployed with Docker Compose:

```bash
docker-compose down
```
This will stop and remove the containers. Add `-v` if you also want to remove named volumes.
