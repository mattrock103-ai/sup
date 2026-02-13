from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import pdfplumber
from docx import Document

SECTION_HEADERS = {
    "summary": ["summary", "profile", "professional summary", "about"],
    "skills": ["skills", "technical skills", "core competencies"],
    "experience": ["experience", "employment", "work experience", "career history"],
    "education": ["education", "academic", "academics"],
    "qualifications": ["qualifications", "certifications", "certificates", "licenses"],
    "additional": ["additional", "additional information", "interests", "projects"],
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/[^\s|,;]+", re.IGNORECASE)


@dataclass
class ParsedCV:
    name: str = ""
    title: str = ""
    location: str = ""
    contact_line: str = ""
    summary: str = ""
    skills: list[str] | str = ""
    experience: list[dict[str, Any]] | str = ""
    education: list[dict[str, Any]] | str = ""
    qualifications: list[str] | str = ""
    certifications: list[str] | str = ""
    additional_info: str = ""


class CVParser:
    @staticmethod
    def extract_text(file_path: Path, file_ext: str) -> list[str]:
        if file_ext == ".docx":
            doc = Document(str(file_path))
            return [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        if file_ext == ".pdf":
            lines: list[str] = []
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    for line in page_text.splitlines():
                        line = line.strip()
                        if line:
                            lines.append(line)
            return lines
        raise ValueError("Unsupported file type for extraction")

    @staticmethod
    def _normalize_header(line: str) -> str:
        return re.sub(r"[^a-z ]", "", line.lower()).strip()

    @classmethod
    def _split_sections(cls, lines: list[str]) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {k: [] for k in SECTION_HEADERS.keys()}
        sections["header"] = []
        current = "header"

        for line in lines:
            normalized = cls._normalize_header(line)
            matched = None
            for key, aliases in SECTION_HEADERS.items():
                if normalized in aliases:
                    matched = key
                    break
            if matched:
                current = matched
                continue
            sections.setdefault(current, []).append(line)

        return sections

    @staticmethod
    def _guess_name(lines: list[str]) -> str:
        for line in lines[:5]:
            if len(line.split()) <= 5 and not EMAIL_RE.search(line) and not PHONE_RE.search(line):
                if re.match(r"^[A-Za-z ,.'-]+$", line.strip()):
                    return line.strip()
        return lines[0].strip() if lines else "Candidate Name"

    @staticmethod
    def _guess_title(lines: list[str], name: str) -> str:
        for line in lines[:8]:
            if line.strip() == name:
                continue
            if any(x in line.lower() for x in ["engineer", "manager", "consultant", "developer", "analyst", "specialist", "director"]):
                return line.strip()
        return ""

    @staticmethod
    def _guess_location(lines: list[str]) -> str:
        for line in lines[:12]:
            if any(token in line.lower() for token in ["uk", "usa", "united", "london", "remote", "city", "county"]):
                if "@" not in line and len(line) < 80:
                    return line.strip()
        return ""

    @staticmethod
    def _build_contact_line(lines: list[str]) -> str:
        text = " | ".join(lines[:25])
        email = EMAIL_RE.search(text)
        phone = PHONE_RE.search(text)
        linkedin = LINKEDIN_RE.search(text)
        bits = []
        if email:
            bits.append(email.group(0))
        if phone:
            bits.append(phone.group(0))
        if linkedin:
            bits.append(linkedin.group(0))
        return " | ".join(dict.fromkeys(bits))

    @staticmethod
    def _extract_bullets(lines: list[str]) -> list[str]:
        bullets = []
        for line in lines:
            if line.startswith(("-", "•", "*")):
                cleaned = re.sub(r"^[-•*]\s*", "", line).strip()
                if cleaned:
                    bullets.append(cleaned)
            elif len(line.split()) > 5:
                bullets.append(line)
        return bullets

    @classmethod
    def _parse_experience(cls, lines: list[str]) -> list[dict[str, Any]]:
        if not lines:
            return []
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        date_re = re.compile(r"(19|20)\d{2}.*(19|20)\d{2}|(19|20)\d{2}.*present", re.IGNORECASE)

        for line in lines:
            if date_re.search(line) and len(line.split()) <= 12:
                if current:
                    entries.append(current)
                current = {
                    "company": "",
                    "title": line,
                    "dates": line,
                    "bullets": [],
                }
                continue

            if current is None:
                current = {
                    "company": "",
                    "title": line,
                    "dates": "",
                    "bullets": [],
                }
                continue

            if not current["company"] and len(line.split()) <= 8 and not line.startswith(("-", "•", "*")):
                current["company"] = line
            elif line.startswith(("-", "•", "*")) or len(line.split()) > 6:
                bullet = re.sub(r"^[-•*]\s*", "", line).strip()
                if bullet:
                    current["bullets"].append(bullet)

        if current:
            entries.append(current)

        return entries

    @classmethod
    def parse(cls, file_path: Path, file_ext: str) -> dict[str, Any]:
        lines = cls.extract_text(file_path, file_ext)
        if not lines:
            raise ValueError("No readable text found in file")

        sections = cls._split_sections(lines)
        name = cls._guess_name(lines)
        title = cls._guess_title(lines, name)
        location = cls._guess_location(lines)
        contact_line = cls._build_contact_line(lines)

        summary_lines = sections["summary"] or sections["header"][2:6]
        summary = "\n".join(summary_lines[:4]).strip()

        skills_lines = sections["skills"]
        skills = cls._extract_bullets(skills_lines) if skills_lines else []
        if not skills and skills_lines:
            joined = " ".join(skills_lines)
            skills = [p.strip() for p in re.split(r"[,|]", joined) if p.strip()]

        experience = cls._parse_experience(sections["experience"])
        if not experience:
            fallback = "\n".join(lines[8:30])
            experience = [{"company": "", "title": "Experience", "dates": "", "bullets": [fallback]}]

        education = []
        for line in sections["education"]:
            if line:
                education.append({"school": line, "degree": "", "dates": ""})

        quals = cls._extract_bullets(sections["qualifications"]) or sections["qualifications"]
        certs = [q for q in quals if "cert" in q.lower()] if isinstance(quals, list) else []

        additional = "\n".join(sections["additional"][:6]).strip()

        parsed = ParsedCV(
            name=name,
            title=title,
            location=location,
            contact_line=contact_line,
            summary=summary or "Professional profile available on request.",
            skills=skills or ["See profile for core capabilities."],
            experience=experience,
            education=education,
            qualifications=quals or [],
            certifications=certs,
            additional_info=additional,
        )
        return asdict(parsed)
