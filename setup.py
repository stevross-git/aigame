from setuptools import setup, find_packages

setup(
    name="ai-sims",
    version="1.0.0",
    description="AI-powered life simulation game with Ollama NPCs",
    author="AI Sims Developer",
    packages=find_packages(),
    install_requires=[
        "pygame==2.5.2",
        "numpy==1.26.4",
        "ollama==0.1.7",
        "requests==2.31.0",
        "chromadb==0.4.22",
        "openai==1.12.0",
        "anthropic==0.7.8",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-sims=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)