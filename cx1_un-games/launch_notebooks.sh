#!/usr/bin/env bash
# Launch all 5 GDP Spurious Regression notebooks via Voilà.
# Usage:
#   ./launch_notebooks.sh          # Launch all notebooks (Voilà, code hidden)
#   ./launch_notebooks.sh jupyter   # Launch in Jupyter (code visible, editable)
#   ./launch_notebooks.sh 3         # Launch only module 3
#   ./launch_notebooks.sh jupyter 2 # Launch module 2 in Jupyter

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_DIR="$SCRIPT_DIR/gdp_env"
NOTEBOOKS_DIR="$SCRIPT_DIR/notebooks"

if [ ! -d "$ENV_DIR" ]; then
    echo "Error: Virtual environment not found at $ENV_DIR"
    echo "Create it with: python3 -m venv gdp_env && gdp_env/bin/pip install -r requirements.txt"
    exit 1
fi

MODE="voila"
MODULE=""

for arg in "$@"; do
    case "$arg" in
        jupyter) MODE="jupyter" ;;
        [1-5])  MODULE="$arg" ;;
        *)      echo "Unknown argument: $arg"; echo "Usage: $0 [jupyter] [1-5]"; exit 1 ;;
    esac
done

NOTEBOOKS=(
    "01_explore_the_data.ipynb"
    "02_overfitting.ipynb"
    "03_regularization.ipynb"
    "04_spurious_features.ipynb"
    "05_cross_validation.ipynb"
)

if [ -n "$MODULE" ]; then
    IDX=$((MODULE - 1))
    SELECTED=("${NOTEBOOKS[$IDX]}")
    echo "Launching Module $MODULE: ${SELECTED[0]}"
else
    SELECTED=("${NOTEBOOKS[@]}")
    echo "Launching all 5 modules"
fi

echo "Mode: $MODE"
echo ""

if [ "$MODE" = "jupyter" ]; then
    echo "Starting Jupyter Notebook server..."
    echo "Navigate to the notebooks/ folder in the browser."
    "$ENV_DIR/bin/jupyter" notebook --notebook-dir="$NOTEBOOKS_DIR"
else
    if [ ${#SELECTED[@]} -eq 1 ]; then
        echo "Starting Voilà for ${SELECTED[0]}..."
        "$ENV_DIR/bin/voila" "$NOTEBOOKS_DIR/${SELECTED[0]}" --no-browser --port=8866
    else
        echo "Starting Voilà server (all notebooks)..."
        echo "Open http://localhost:8866 in your browser and pick a module."
        "$ENV_DIR/bin/voila" "$NOTEBOOKS_DIR" --no-browser --port=8866
    fi
fi
