#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing GitHub Copilot CLI..."
npm install -g @github/copilot

echo "Installing Marp CLI..."
npm install -g @marp-team/marp-cli

echo "Post-create setup complete."