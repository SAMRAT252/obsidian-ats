document.addEventListener('DOMContentLoaded', () => {
    // Check if dropZone exists
    const dropZone = document.getElementById('dropZone') || document.getElementById('drop-zone');
    const fileInput = document.getElementById('resumeFile') || document.getElementById('resume-file');
    const fileInfo = document.getElementById('fileInfo') || document.getElementById('file-info');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadBtn = document.getElementById('uploadBtn') || document.querySelector('button[type="submit"]');
    const removeFile = document.getElementById('removeFile');

    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }

    function handleFile(file) {
        if (!file) return;
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['pdf', 'docx'].includes(ext)) {
            alert('Only PDF and DOCX files are allowed.');
            if (fileInput) fileInput.value = '';
            return;
        }
        if (file.size > 16 * 1024 * 1024) {
            alert('File size exceeds the 16MB limit.');
            if (fileInput) fileInput.value = '';
            return;
        }

        if (fileName) fileName.textContent = file.name;
        if (fileSize) fileSize.textContent = formatBytes(file.size);
        if (fileInfo) fileInfo.style.display = 'block';
        if (dropZone) dropZone.style.display = 'none';
        if (uploadBtn) uploadBtn.disabled = false;
    }

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                handleFile(this.files[0]);
            }
        });
    }

    if (removeFile && fileInput) {
        removeFile.addEventListener('click', function() {
            fileInput.value = '';
            if (fileInfo) fileInfo.style.display = 'none';
            if (dropZone) dropZone.style.display = 'block';
            if (uploadBtn) uploadBtn.disabled = true;
        });
    }

    if (dropZone && fileInput) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            if (e.dataTransfer && e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFile(e.dataTransfer.files[0]);
            }
        });
    }

    const uploadForm = document.getElementById('uploadForm') || document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', () => {
            if (uploadBtn) {
                uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
                uploadBtn.disabled = true;
            }
        });
    }
});
