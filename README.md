# City Information Assistant API

A production-ready FastAPI backend for the City Information Assistant, providing information about cities worldwide including weather, local time, and interesting facts.

## Features

- **FastAPI** for high-performance async API endpoints
- **LangChain** for LLM integration and tool orchestration
- **Pydantic** for data validation and settings management
- **Async HTTP client** with retry logic and error handling
- **LangSmith** integration for observability and tracing
- **Streaming responses** for real-time chat interactions
- **Modular architecture** for maintainability and scalability
- **Comprehensive error handling** with custom exceptions
- **Production-ready** with proper logging and monitoring

## Getting Started

### Prerequisites

- Python 3.9+
- pip
- OpenAI API key
- (Optional) OpenWeatherMap API key
- (Optional) GeoDB API key
- (Optional) LangSmith API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hiteshkalwani/SM-Assignment.git
   cd SM-Assignment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   # Using pip
   pip install -r requirements.txt

   # Or using Poetry
   poetry install
   ```

4. Create a `.env` file in the project root with your API keys:
   ```env
   # Required
   OPENAI_API_KEY=your_openai_api_key

   # Optional
   OPENWEATHER_API_KEY=your_openweather_api_key
   GEODB_API_KEY=your_geodb_api_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=city-information-assistant

   # App settings
   ENVIRONMENT=development
   DEBUG=true
   LOG_LEVEL=INFO
   ```

### Running the Application

#### Docker Compose (Recommended)

```bash
# Start all services (backend + nginx load balancer)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and restart services
docker-compose up -d --build

# Scale backend replicas (default is 3)
docker-compose up -d --scale backend=5

# Development mode with live reload
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

The API will be available at `http://localhost:80` / `http://localhost` (via Nginx load balancer)

#### Direct Python Development

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server (with Gunicorn)
gunicorn -k uvicorn.workers.UvicornWorker app.main:app
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:80/docs`
- **ReDoc**: `http://localhost:80/redoc`
- **OpenAPI Schema**: `http://localhost:80/openapi.json`

## Project Structure

```
SM-Assignment/
├── README.md                           # Main project documentation
├── docker-compose.yml                  # Docker orchestration for the project
│
└── city-assistant-backend/             # Backend application directory
    ├── Dockerfile                      # Container configuration
    ├── .dockerignore                   # Docker build exclusions
    ├── requirements.txt                # Python dependencies
    ├── setup.py                       # Package setup configuration
    ├── pytest.ini                     # Test configuration
    ├── conftest.py                     # Shared test fixtures
    │
    ├── app/                            # Main application code
    │   ├── __init__.py
    │   ├── main.py                     # FastAPI application entry point
    │   │
    │   ├── agents/                     # AI agent implementations
    │   │   ├── __init__.py
    │   │   ├── base_agent.py           # Base agent class
    │   │   └── city_agent.py           # City-specific agent
    │   │
    │   ├── api/                        # API layer (FastAPI routers)
    │   │   ├── __init__.py
    │   │   └── v1/                     # API version 1
    │   │       ├── __init__.py
    │   │       ├── router.py           # Main API router
    │   │       ├── chat.py             # Chat endpoints
    │   │       └── health.py           # Health check endpoint
    │   │
    │   ├── core/                       # Core application components
    │   │   ├── config.py               # Configuration management
    │   │   ├── llm.py                  # LLM client wrapper
    │   │   ├── logging.py              # Logging configuration
    │   │   └── observability.py        # LangSmith tracing
    │   │
    │   ├── tools/                      # Tool implementations
    │   │   ├── __init__.py
    │   │   ├── facts_tool.py           # City facts retrieval
    │   │   ├── plan_visit_tool.py      # Visit planning tool
    │   │   ├── time_tool.py            # Time zone information
    │   │   └── weather_tool.py         # Weather information
    │   │
    │   └── utils/                      # Utility functions
    │       ├── exceptions.py           # Custom exception classes
    │       └── http_client.py          # HTTP client utilities
    │
    ├── tests/                          # Unit and integration tests
    │   ├── conftest.py                 # Test fixtures and configuration
    │   ├── test_agents.py              # Agent functionality tests
    │   ├── test_api.py                 # API endpoint tests
    │   ├── test_config.py              # Configuration tests
    │   ├── test_exceptions.py          # Exception handling tests
    │   ├── test_integration.py         # End-to-end integration tests
    │   └── test_tools.py               # Tool implementation tests
    │
    └── logs/                           # Application logs directory
```

## API Endpoints

### Health Check

- `GET /health` - Check the health status of the service and its dependencies
- `GET /docs` - Swagger UI

### Chat

- `POST /api/v1/chat` - Chat with the City Information Assistant
- `GET /api/v1/chat/stream` - Stream chat responses (SSE)

### Example Request

- Chat with the City Information Assistant

```bash
curl -X 'POST' \
  'http://localhost:80/api/v1/chat' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role": "user", "content": "What\'s the weather like in London?"}
    ],
  }'
```

- Stream chat responses (SSE)

```bash
curl --location 'http://localhost:80/api/v1/chat/' \
--header 'Content-Type: application/json' \
--data '{
  "messages": [
    {"role": "user", "content": "plan my visit to tokyo?"}
  ],
  "stream": true
}'
```

```bash
curl --location 'http://localhost:80/api/v1/chat/stream?message=plan%20my%20visit%20to%20Jamnagar' \
--data ''
```

## Deployment

### Docker with Nginx Load Balancing

The application includes production-ready Nginx load balancing for high availability and scalability.

#### Architecture

```
Internet → Nginx (Port 80) → Load Balancer → Backend Service (3 Replicas)
                                          ├── city-assistant-backend (replica 1)
                                          ├── city-assistant-backend (replica 2)
                                          └── city-assistant-backend (replica 3)
```

#### Quick Start with Load Balancing

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

2. **Deploy with load balancing:**
   ```bash
   # Production with 3 backend replicas + Nginx
   docker-compose up -d

   # Scale to different number of replicas
   docker-compose up -d --scale city-assistant-backend=5

   # Development mode (single instance, no load balancer)
   docker-compose --profile dev up -d city-assistant-dev
   ```

3. **Access the application:**
   - **Load Balanced API**: `http://localhost` (port 80)
   - **Direct Development**: `http://localhost:8001`
   - **API Documentation**: `http://localhost/docs`

#### Load Balancing Features

**🔄 Load Balancing Algorithm:**
- **Least Connections** - Routes to server with fewest active connections
- **Health Checks** - Automatic failover for unhealthy instances
- **Backup Server** - Fallback instance for high availability

**⚡ Performance Optimizations:**
- **Gzip Compression** - Reduces response size by ~70%
- **Connection Pooling** - Efficient upstream connections
- **Request Buffering** - Optimized for different endpoint types

**🛡️ Security & Rate Limiting:**
- **Rate Limiting**: 10 req/s for API, 5 req/s for streaming
- **Security Headers**: XSS protection, content type validation
- **CORS Support**: Configurable cross-origin requests

**📊 Monitoring:**
- **Nginx Status**: `http://localhost/nginx-status`
- **Health Checks**: `http://localhost/health`
- **Access Logs**: `./nginx/logs/access.log`

#### Configuration Files

```
nginx/
├── nginx.conf          # Main Nginx configuration
├── Dockerfile          # Custom Nginx container
└── logs/              # Nginx access and error logs
```

### Docker (Single Instance)

For development or small deployments without load balancing:
```bash
# Build the Docker image
docker build -t city-assistant-backend ./city-assistant-backend

# Run the container
docker run -d \
  --name city-assistant \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  city-assistant-backend
```

#### Docker Services

- **city-assistant-backend**: Production service on port 8000
- **city-assistant-dev**: Development service with hot reload on port 8001

#### Environment Variables

All environment variables from `.env.example` are supported:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
GEODB_API_KEY=your_geodb_api_key_here

# Optional
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
```

#### Health Checks

The Docker containers include built-in health checks:
- Endpoint: `GET /health`
- Interval: 30 seconds
- Timeout: 10 seconds

#### Logs

Container logs are mounted to `./logs` directory for persistence.

```bash
# View logs
docker-compose logs -f city-assistant-backend

# View development logs
docker-compose logs -f city-assistant-dev
```

## Development

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for static type checking
- **ruff** for linting

Run the following commands to ensure code quality:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
ruff check .

# Type checking
mypy .
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [OpenAI](https://openai.com/)
- [LangSmith](https://smith.langchain.com/)
