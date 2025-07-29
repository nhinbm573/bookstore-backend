#!/bin/bash

echo "🔧 Setting up your Django development environment..."

# 1. Create virtual environment
if [ ! -d "env" ]; then
  echo "📦 Creating virtual environment..."
  python3.11 -m venv venv
else
  echo "✅ Virtual environment already exists."
fi

# 2. Activate virtual environment
echo "🐍 Activating virtual environment..."
source env/bin/activate

# 3. Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# 4. Install requirements
echo "📚 Installing project dependencies..."
pip install -r requirements-dev.txt

# 5. Install pre-commit hook
echo "⛓️ Installing pre-commit hook..."
pre-commit install

echo "✅ All set! You can now run the server with:"
echo "   source env/bin/activate && python manage.py runserver"
