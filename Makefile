.PHONY: install test run clean setup-dev docker help

# Default target
help:
	@echo "🎮 AI Sims - Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install    - Full installation (Python deps + Ollama + AI model)"
	@echo "  make setup-dev  - Development setup (deps only)"
	@echo "  make test       - Run all tests to verify setup"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run        - Start the game"
	@echo "  make run-debug  - Start with debug output"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker     - Build and run in Docker"
	@echo "  make docker-build - Build Docker image only"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Clean temporary files and cache"
	@echo "  make reset      - Reset game data (saves, memories)"
	@echo ""

# Installation
install:
	@echo "🚀 Starting full installation..."
	@chmod +x install.sh
	@./install.sh

setup-dev:
	@echo "📦 Installing Python dependencies..."
	@pip3 install -r requirements.txt
	@mkdir -p chroma_db assets/sprites assets/maps
	@echo "✅ Development setup complete"

# Testing
test:
	@echo "🧪 Running setup tests..."
	@python3 test_setup.py

# Running
run:
	@echo "🎮 Starting AI Sims..."
	@chmod +x run.sh
	@./run.sh

run-debug:
	@echo "🐛 Starting AI Sims with debug output..."
	@PYTHONPATH=. python3 -u main.py

run-direct:
	@echo "🎮 Starting AI Sims directly..."
	@python3 main.py

# Docker
docker:
	@echo "🐳 Building and running Docker container..."
	@docker-compose up --build

docker-build:
	@echo "🐳 Building Docker image..."
	@docker build -t ai-sims .

# Maintenance
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.tmp" -delete 2>/dev/null || true
	@find . -type f -name "*.bak" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

reset:
	@echo "⚠️  Resetting game data..."
	@rm -f game_memories.db savegame.json
	@rm -rf chroma_db/*
	@echo "✅ Game data reset"

# Development helpers
lint:
	@echo "🔍 Running code linting..."
	@python3 -m flake8 src/ --max-line-length=100 --ignore=E203,W503 || echo "flake8 not installed"

format:
	@echo "🎨 Formatting code..."
	@python3 -m black src/ --line-length=100 || echo "black not installed"

# Dependencies
update-deps:
	@echo "⬆️  Updating dependencies..."
	@pip3 install --upgrade -r requirements.txt

freeze-deps:
	@echo "❄️  Freezing dependencies..."
	@pip3 freeze > requirements-frozen.txt

# Ollama management
ollama-start:
	@echo "🤖 Starting Ollama service..."
	@ollama serve &

ollama-pull:
	@echo "📥 Downloading AI models..."
	@ollama pull llama2
	@ollama pull llama2:7b

ollama-stop:
	@echo "🛑 Stopping Ollama service..."
	@pkill ollama || true

# Package
package:
	@echo "📦 Creating distribution package..."
	@python3 setup.py sdist bdist_wheel

# Quick development cycle
dev: setup-dev test run-debug

# Full setup and test
full: install test run