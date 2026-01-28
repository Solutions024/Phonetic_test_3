# Docker Setup

## Build

```bash
docker build -t phonetic-match-api .
```

## Run

```bash
docker run -d -p 8000:8000 phonetic-match-api
```

## Access

Open `http://localhost:8000` in your browser.

## Stop

```bash
docker ps
docker stop <container_id>
```
