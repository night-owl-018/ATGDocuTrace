# ATGDocuTrace

ATGDocuTrace is a Docker-ready OCR service for Unraid built with PaddleOCR. It accepts PDF and image uploads, runs OCR, and stores the original file plus extracted data for later use.

## Features

- PDF and image OCR
- Persistent storage for uploads, pages, text, and raw OCR JSON
- SQLite job history
- FastAPI API
- Unraid-friendly volume mapping

## Stored Data

Everything is saved under `/app/data`:

- `uploads/` original uploaded files
- `pages/` rendered PDF pages or normalized images
- `results/` raw OCR JSON
- `text/` extracted plain text
- `database/` SQLite database

## API

### Health check

`GET /health`

### Submit OCR job

`POST /ocr`

Form field: `file`

### List jobs

`GET /jobs`

### Get one job

`GET /jobs/{job_id}`

## Local Docker Usage

Build:

```bash
docker build -t atgdocutrace .
```

Run:

```bash
docker run -d \
  --name atgdocutrace \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  atgdocutrace
```

Open API docs:

```text
http://localhost:8080/docs
```

## Unraid Volume Mapping

Map this container path:

- `/app/data`

To a host path such as:

- `/mnt/user/appdata/atgdocutrace`

## Example OCR Request

```bash
curl -X POST "http://localhost:8080/ocr" \
  -F "file=@/path/to/document.pdf"
```

## Notes

This version is CPU-based for easier Unraid setup. Rebuilding the image can pull newer PaddleOCR versions if you update `requirements.txt`.
