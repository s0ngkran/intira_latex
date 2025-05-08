#!/bin/bash

# Read the content of main.tex and escape it for JSON
TEX_CONTENT=$(python3 -c 'import json,sys; print(json.dumps({"tex_content": open("main.tex", encoding="utf-8").read()}))')

# Send the request and save the PDF
curl -X POST http://localhost:9200/compile \
  -H "Content-Type: application/json" \
  -d "$TEX_CONTENT" \
  --output result.pdf

echo "PDF saved as result.pdf"
