FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md README.zh-CN.md LICENSE CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md ./
COPY termloop ./termloop

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["termloop"]

