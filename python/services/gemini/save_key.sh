#!/bin/bash

# Check for ~/.gcp directory
if [ ! -d ~/.gcp ]; then
  # Create the directory if it doesn't exist
  mkdir ~/.gcp
  echo "Created directory: ~/.gcp"
fi

# Prompt for API key
read -p "Enter your Gemini API key: " api_key

# Write the API key to the file (with error handling)
if echo "$api_key" > ~/.gcp/gemini.key; then
  echo export GEMINI_KEY="$api_key" >> ~/.bashrc
  source ~/.bashrc
  echo "API key saved successfully to: ~/.gcp/gemini.key and env variable GEMINI_API_KEY"
else
  echo "Error saving API key. Please check file permissions."
fi

