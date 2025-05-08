FROM python:3.11-slim

# Install TeX Live and basic packages
RUN apt-get update && \
    apt-get install -y texlive-xetex texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9200

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9200"] 