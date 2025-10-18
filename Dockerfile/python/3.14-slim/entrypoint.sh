#!/bin/sh
set -euo pipefail

if [ -f "requirements.txt" ]; then
    echo "Initializing Python environment..."

    # Get Python version for venv directory naming
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
    VENV_DIR=".venv-${PYTHON_VERSION}"

    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment for Python ${PYTHON_VERSION}..."
        python3 -m venv "$VENV_DIR" || { echo "Failed to create virtual environment"; exit 1; }
    fi

    . "$VENV_DIR/bin/activate" || { echo "Failed to activate virtual environment"; exit 1; }

    CURRENT_HASH=$(sha256sum requirements.txt | cut -d' ' -f1)
    HASH_FILE="$VENV_DIR/requirements.sha256"

    REINSTALL=false
    if [ ! -f "$HASH_FILE" ]; then
        echo "Installing dependencies..."
        REINSTALL=true
    else
        STORED_HASH=$(cat "$HASH_FILE")
        if [ "$CURRENT_HASH" != "$STORED_HASH" ]; then
            echo "Dependencies changed, updating..."
            REINSTALL=true
        fi
    fi

    if [ "$REINSTALL" = true ]; then
        pip freeze | grep -v -E "^(pip|setuptools|wheel)=" | xargs -r pip uninstall -y || true
        pip install -r requirements.txt || { echo "Failed to install requirements"; exit 1; }
        echo "$CURRENT_HASH" > "$HASH_FILE" || { echo "Failed to save hash"; exit 1; }
        echo "Environment ready"
    fi
fi

if [ $# -gt 0 ]; then
    exec "$@"
else
    exec python main.py
fi
