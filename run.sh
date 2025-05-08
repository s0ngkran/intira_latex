docker run -p 9200:9200 \
  -v "$(pwd)/latex_api/main.py:/app/main.py" \
  -v "$(pwd)/latex_api/requirements.txt:/app/requirements.txt" \
  -v "$(pwd)/assets:/app/assets" \
  --workdir /app \
  latex-api