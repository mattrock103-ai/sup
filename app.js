const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const statusNode = document.getElementById('status');
const downloadBtn = document.getElementById('downloadBtn');
const clearBtn = document.getElementById('clearBtn');

const nameNode = document.getElementById('candidateName');
const contactNode = document.getElementById('candidateContact');
const profileNode = document.getElementById('profileText');
const skillsList = document.getElementById('skillsList');
const experienceList = document.getElementById('experienceList');
const educationList = document.getElementById('educationList');

browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (event) => {
  const file = event.target.files?.[0];
  if (file) {
    void processFile(file);
  }
});

['dragenter', 'dragover'].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove('dragover');
  });
});

dropzone.addEventListener('drop', (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    void processFile(file);
  }
});

clearBtn.addEventListener('click', () => {
  nameNode.textContent = 'Candidate Name';
  contactNode.textContent = 'contact@email.com | 07xxx xxxxxx | Location';
  profileNode.textContent = 'Candidate summary will appear here.';
  skillsList.innerHTML = '';
  experienceList.innerHTML = '';
  educationList.innerHTML = '';
  statusNode.textContent = 'Cleared.';
  downloadBtn.disabled = true;
  clearBtn.disabled = true;
});

downloadBtn.addEventListener('click', () => {
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Formatted CV</title></head><body>${document.getElementById('cvTemplate').outerHTML}</body></html>`;
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'churchill-howard-formatted-cv.html';
  anchor.click();
  URL.revokeObjectURL(url);
});

async function processFile(file) {
  statusNode.textContent = `Reading ${file.name}...`;

  try {
    const text = await extractText(file);
    const formatted = mapToChurchillHowardTemplate(text);
    renderFormattedCV(formatted);
    statusNode.textContent = `Formatted ${file.name} successfully.`;
    downloadBtn.disabled = false;
    clearBtn.disabled = false;
  } catch (error) {
    console.error(error);
    statusNode.textContent = 'Could not parse this file. Please try a .docx, .pdf, or .txt CV.';
  }
}

async function extractText(file) {
  const extension = file.name.split('.').pop()?.toLowerCase();

  if (extension === 'txt') {
    return file.text();
  }

  if (extension === 'docx') {
    const buffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer: buffer });
    return result.value;
  }

  if (extension === 'pdf') {
    const buffer = await file.arrayBuffer();
    const pdfjsLib = await import('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.min.mjs');
    const pdf = await pdfjsLib.getDocument({ data: buffer }).promise;
    const pages = [];

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
      const page = await pdf.getPage(pageNum);
      const content = await page.getTextContent();
      pages.push(content.items.map((item) => item.str).join(' '));
    }

    return pages.join('\n');
  }

  throw new Error('Unsupported file type');
}

function mapToChurchillHowardTemplate(rawText) {
  const text = rawText.replace(/\r/g, '');
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean);

  const name = guessName(lines);
  const contact = extractContact(text);
  const profile = extractSection(text, ['profile', 'summary', 'professional summary']) || lines.slice(2, 6).join(' ');
  const skills = extractListSection(text, ['skills', 'core skills', 'key skills']);
  const experience = extractExperience(text);
  const education = extractListSection(text, ['education', 'qualifications', 'certifications']);

  return {
    name,
    contact,
    profile,
    skills: skills.length ? skills : ['Stakeholder management', 'Communication', 'Commercial awareness'],
    experience: experience.length
      ? experience
      : [{ title: 'Role title not detected', meta: 'Company | Dates', bullets: ['Please edit this section manually.'] }],
    education: education.length ? education : ['Education details were not detected.']
  };
}

function guessName(lines) {
  const firstNonEmpty = lines.find((line) => line.length > 3) || 'Candidate Name';
  return firstNonEmpty.replace(/[^a-zA-Z\-\s]/g, '').trim() || 'Candidate Name';
}

function extractContact(text) {
  const email = text.match(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i)?.[0];
  const phone = text.match(/(\+?\d[\d\s().-]{8,}\d)/)?.[0];
  const location = text.match(/\b(london|manchester|birmingham|leeds|bristol|remote)\b/i)?.[0];
  return [email || 'email not found', phone || 'phone not found', location || 'location not found'].join(' | ');
}

function extractSection(text, sectionNames) {
  for (const sectionName of sectionNames) {
    const regex = new RegExp(`${sectionName}\\s*[:\\n]([\\s\\S]*?)(?:\\n[A-Z][A-Za-z &]{2,}|$)`, 'i');
    const matched = text.match(regex);
    if (matched?.[1]) {
      return matched[1].trim().split('\n').slice(0, 4).join(' ');
    }
  }
  return '';
}

function extractListSection(text, sectionNames) {
  const section = extractSection(text, sectionNames);
  if (!section) {
    return [];
  }

  return section
    .split(/\n|•|-|\u2022/)
    .map((item) => item.trim())
    .filter((item) => item.length > 2)
    .slice(0, 8);
}

function extractExperience(text) {
  const section = extractSection(text, ['experience', 'employment history', 'work history', 'career history']);
  if (!section) {
    return [];
  }

  const blocks = section
    .split(/\n\n+/)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .slice(0, 5);

  return blocks.map((block) => {
    const chunkLines = block.split('\n').map((line) => line.trim()).filter(Boolean);
    const title = chunkLines[0] || 'Role';
    const meta = chunkLines[1] || 'Company | Dates';
    const bullets = chunkLines.slice(2).filter((line) => line.length > 6);

    return {
      title,
      meta,
      bullets: bullets.length ? bullets : ['Achievement details not automatically extracted.']
    };
  });
}

function renderFormattedCV(data) {
  nameNode.textContent = data.name;
  contactNode.textContent = data.contact;
  profileNode.textContent = data.profile;

  skillsList.innerHTML = data.skills.map((skill) => `<li>${escapeHtml(skill)}</li>`).join('');

  experienceList.innerHTML = data.experience
    .map(
      (job) => `
      <div class="job">
        <div class="job-title">${escapeHtml(job.title)}</div>
        <div class="job-meta">${escapeHtml(job.meta)}</div>
        <ul>${job.bullets.map((bullet) => `<li>${escapeHtml(bullet)}</li>`).join('')}</ul>
      </div>`
    )
    .join('');

  educationList.innerHTML = data.education.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
