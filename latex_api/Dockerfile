FROM python:3.11-slim

# Install certificates and update package lists
RUN apt-get update && \
    apt-get install -y ca-certificates gnupg2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure apt repositories
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list && \
    echo "deb http://security.debian.org/debian-security bullseye-security main" >> /etc/apt/sources.list

# Install TeX Live and basic packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9200

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9200"] 