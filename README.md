# Todo Console Application

A console-based todo application implementing CRUD operations with in-memory storage for Phase I learning objectives.

## Setup

1. Ensure you have Python 3.13+ installed
2. Install UV package manager: `pip install uv`
3. Install dependencies: `uv sync` (or `pip install -e .` if using pip)

## Usage

Run the application with:
```
python src/main.py
```

## Features

- Add new todo tasks with title and optional description
- View all tasks with status indicators
- Update existing tasks
- Delete tasks with confirmation
- Mark tasks as complete/incomplete

## Architecture

This Phase I implementation uses:
- Python 3.13+ with standard library only
- In-memory storage (no persistent storage)
- Console interface only (no web/GUI components)
- Clean code principles following PEP 8