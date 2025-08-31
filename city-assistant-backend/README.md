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
- [Poetry](https://python-poetry.org/) (recommended) or pip
- OpenAI API key
- (Optional) OpenWeatherMap API key
- (Optional) GeoDB API key
- (Optional) LangSmith API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/city-assistant-backend.git
   cd city-assistant-backend
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

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server (with Gunicorn)
gunicorn -k uvicorn.workers.UvicornWorker app.main:app
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Project Structure

```
city-assistant-backend/
├── app/                    # Application code
│   ├── api/                # API layer (FastAPI routers)
│   │   └── v1/             # API version 1
│   │       ├── chat.py     # Chat endpoints
│   │       └── health.py   # Health check endpoint
│   │
│   ├── core/               # Core application components
│   │   ├── config.py      # Configuration management
│   │   ├── llm.py         # LLM client wrapper
│   │   ├── logging.py     # Logging configuration
│   │   └── observability.py # LangSmith tracing
│   │
│   ├── models/            # Database models (future use)
│   ├── tools/             # Tool implementations
│   └── utils/             # Utility functions
│
├── tests/                 # Unit and integration tests
├── .env.example          # Example environment variables
├── .gitignore
├── poetry.lock           # Poetry lock file
├── pyproject.toml        # Project metadata and dependencies
└── README.md             # This file
```

## API Endpoints

### Health Check

- `GET /health` - Check the health status of the service and its dependencies

### Chat

- `POST /api/v1/chat` - Chat with the City Information Assistant
- `GET /api/v1/chat/stream` - Stream chat responses (SSE)

### Example Request

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/chat' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [
      {"role": "user", "content": "What\'s the weather like in London?"}
    ],
    "city": "London",
    "country": "UK",
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
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

## Deployment

### Docker

```bash
# Build the Docker image
docker build -t city-assistant-backend .

# Run the container
docker run -p 8000:8000 --env-file .env city-assistant-backend
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
