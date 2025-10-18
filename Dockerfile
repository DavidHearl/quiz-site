FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for psycopg, lxml, cryptography, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    postgresql-client \
    wget ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# upgrade toolchain (compatible with old pins) then install your deps
COPY requirements.txt .

# DEBUG: show the requirements file seen inside the image
RUN echo "=== requirements.txt inside image ===" && sed -n '1,200p' requirements.txt

# DEBUG: show python/pip versions too
RUN python -V && pip -V

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# app code
COPY . .

# run with gunicorn on port 8000
CMD ["gunicorn","quiz.wsgi:application","-w","3","-b",":8000"]
