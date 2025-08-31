"""Setup configuration for City Information Assistant."""

from setuptools import setup, find_packages

setup(
    name="city-assistant-backend",
    version="1.0.0",
    description="City Information Assistant Backend API",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.11.6",
        "pydantic-settings==2.10.1",
        "langchain==0.3.27",
        "langchain-openai==0.3.32",
        "langchain-community==0.3.29",
        "openai==1.102.0",
        "httpx==0.25.2",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "pytest-cov==4.1.0",
        "loguru==0.7.2",
        "requests==2.32.5",
        "python-dateutil==2.8.2",
    ],
    extras_require={
        "dev": [
            "black>=23.9.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
)
