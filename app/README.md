# CV House-Style Formatter (MVP)

A local-first FastAPI app that formats incoming CVs into a **DOCX house style template** using deterministic placeholders.

## Features
- Upload and save one active template: `POST /api/template/upload` (`/app/data/template.docx`)
- Format CV input (`.docx` or `.pdf`) into template placeholders: `POST /api/cv/format`
- Optional parsing debug endpoint: `POST /api/parse/preview`
- Single-page frontend with:
  - Upload House Style CV
  - Upload New CV
  - Format CV button
  - Download Result link
- Security basics:
  - file size limits
  - extension validation
  - uploads stored under `/app/data/uploads`
  - no file execution

---

## Project structure

```
/app
  /backend
    main.py
    parser.py
    formatter.py
    storage.py
    requirements.txt
  /frontend
    index.html
    app.js
    styles.css
  /templates
    base_template.docx (auto-generated on first start)
  /data
    (runtime storage; bind mount in Docker)
  Dockerfile
  docker-compose.yml
  README.md
```

---

## Local run (Python venv)

From the `/app` folder:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000`

---

## Docker run

From `/app`:

```bash
docker compose up --build
```

Open: `http://localhost:8000`

Data persists via bind mount:
- host `./data` -> container `/app/data`

---

## How template-driven formatting works

The uploaded “House Style CV” is used directly as the template source-of-truth.

### Required placeholders in template DOCX

Use these exact placeholders somewhere in your DOCX:

- `{{NAME}}`
- `{{TITLE}}`
- `{{LOCATION}}`
- `{{CONTACT_LINE}}`
- `{{SUMMARY}}`
- `{{SKILLS}}`
- `{{EXPERIENCE}}`
- `{{EDUCATION}}`
- `{{QUALIFICATIONS}}`
- `{{CERTIFICATIONS}}`
- `{{ADDITIONAL_INFO}}`

### Recommended template setup

1. Build a styled DOCX in Word with your real branding/styles.
2. Put the placeholders in the exact sections where content should appear.
3. For bullet sections (`SKILLS`, `QUALIFICATIONS`, `CERTIFICATIONS`), set the placeholder paragraph style to your bullet style.
4. Save as `.docx` and upload it via the UI as “House Style CV”.

If no uploaded template exists, app falls back to auto-generated `/app/templates/base_template.docx`.

---

## API quick reference

### 1) Upload template

```bash
curl -X POST "http://localhost:8000/api/template/upload" \
  -F "file=@house_style_template.docx"
```

### 2) Check template status

```bash
curl "http://localhost:8000/api/template/status"
```

### 3) Format CV

```bash
curl -X POST "http://localhost:8000/api/cv/format" \
  -F "file=@input_cv.pdf" \
  --output formatted_cv.docx
```

### 4) Parse preview (optional)

```bash
curl -X POST "http://localhost:8000/api/parse/preview" \
  -F "file=@input_cv.docx"
```

---

## Notes for MVP parsing

Parser performs best-effort extraction for:
- name, contact, location
- summary
- skills
- experience
- education
- qualifications/certs

If parsing is uncertain, fallback text is still populated so formatting always returns a DOCX.

