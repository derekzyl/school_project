#!/bin/bash

# Install Python dependencies
pip install --no-cache-dir --upgrade -r requirements.txt

# Install Node.js dependencies
npm install -g pnpm

pnpm i

# Build the TypeScript code
pnpm run build

# Start both servers concurrently
concurrently "uvicorn main:app --reload --host 0.0.0.0 --port 8000" "vite"

# Note: Make sure to give execute permissions to the script: chmod +x run_app.sh
echo 'server started successfully'