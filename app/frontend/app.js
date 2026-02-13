const templateInput = document.getElementById('templateFile');
const cvInput = document.getElementById('cvFile');
const uploadTemplateBtn = document.getElementById('uploadTemplateBtn');
const formatBtn = document.getElementById('formatBtn');
const previewBtn = document.getElementById('previewBtn');
const templateStatus = document.getElementById('templateStatus');
const formatStatus = document.getElementById('formatStatus');
const downloadLink = document.getElementById('downloadLink');
const previewBox = document.getElementById('previewBox');

async function checkTemplateStatus() {
  try {
    const res = await fetch('/api/template/status');
    const data = await res.json();
    if (data.exists) {
      templateStatus.textContent = 'Template saved ✅';
      templateStatus.className = 'status ok';
    } else {
      templateStatus.textContent = 'No template uploaded yet.';
      templateStatus.className = 'status';
    }
  } catch (err) {
    templateStatus.textContent = `Could not check template status: ${err.message}`;
    templateStatus.className = 'status err';
  }
}

uploadTemplateBtn.addEventListener('click', async () => {
  const file = templateInput.files[0];
  if (!file) {
    templateStatus.textContent = 'Please choose a .docx template first.';
    templateStatus.className = 'status err';
    return;
  }

  const fd = new FormData();
  fd.append('file', file);

  templateStatus.textContent = 'Uploading template...';
  templateStatus.className = 'status';

  try {
    const res = await fetch('/api/template/upload', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Upload failed');
    templateStatus.textContent = 'Template saved ✅';
    templateStatus.className = 'status ok';
  } catch (err) {
    templateStatus.textContent = `Template upload failed: ${err.message}`;
    templateStatus.className = 'status err';
  }
});

formatBtn.addEventListener('click', async () => {
  const file = cvInput.files[0];
  if (!file) {
    formatStatus.textContent = 'Please choose a CV file (.docx or .pdf).';
    formatStatus.className = 'status err';
    return;
  }

  const fd = new FormData();
  fd.append('file', file);

  formatStatus.textContent = 'Formatting CV...';
  formatStatus.className = 'status';
  downloadLink.classList.add('hidden');

  try {
    const res = await fetch('/api/cv/format', { method: 'POST', body: fd });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || 'Formatting failed');
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.classList.remove('hidden');
    formatStatus.textContent = 'Formatting complete ✅';
    formatStatus.className = 'status ok';
  } catch (err) {
    formatStatus.textContent = `Format failed: ${err.message}`;
    formatStatus.className = 'status err';
  }
});

previewBtn.addEventListener('click', async () => {
  const file = cvInput.files[0];
  if (!file) {
    formatStatus.textContent = 'Please choose a CV file first for preview.';
    formatStatus.className = 'status err';
    return;
  }

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await fetch('/api/parse/preview', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Preview failed');
    previewBox.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    formatStatus.textContent = `Preview failed: ${err.message}`;
    formatStatus.className = 'status err';
  }
});

checkTemplateStatus();
