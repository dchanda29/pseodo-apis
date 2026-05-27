FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY pseudo_apis ./pseudo_apis

RUN pip install --no-cache-dir .

EXPOSE 8010

CMD ["uvicorn", "pseudo_apis.main:app", "--host", "0.0.0.0", "--port", "8010"]

