# Churchill Howard CV Formatter

A lightweight browser app that lets recruiters drag-and-drop a CV (`.docx`, `.pdf`, `.txt`) and automatically reshape it into a consistent Churchill Howard house format.

## Features

- Drag-and-drop and file-picker upload
- Extract text from DOCX (Mammoth), PDF (pdf.js), and plain text
- Detect likely CV sections (name, profile, skills, experience, education)
- Render into a fixed Churchill Howard template preview
- Download the formatted result as an HTML file

## Run locally

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Notes

- CV parsing is heuristic-based; extracted sections may need manual tweaks.
- The template is intentionally opinionated so all output stays consistent.
