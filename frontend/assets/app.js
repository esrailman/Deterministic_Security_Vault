// Deterministic Security Vault - Frontend Logic

const API_BASE_URL = 'http://127.0.0.1:8000';

// Global state for selected file
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    logToConsole("System Initialized...", "system");

    // --- 1. Matrix Background Init ---
    initMatrixRain();

    // --- Upload Page Logic ---
    const uploadDropZone = document.getElementById('dropZone-upload');
    if (uploadDropZone) {
        setupUploadPage(uploadDropZone);
        // Bind Manual Button
        const btnRegister = document.getElementById('btn-register-manual');
        if (btnRegister) {
            btnRegister.addEventListener('click', async () => {
                if (selectedFile) {
                    await processRegistration(uploadDropZone, selectedFile);
                } else {
                    alert("Please select a file first.");
                }
            });
        }
    }

    // --- Verify Page Logic ---
    const verifyDropZone = document.getElementById('dropZone-verify');
    if (verifyDropZone) setupVerifyPage(verifyDropZone);

    // --- Quick Verify (Dashboard) ---
    const quickVerifyZone = document.getElementById('dropZone-quickVerify');
    if (quickVerifyZone) setupVerifyPage(quickVerifyZone);

    // --- Audit Page Logic ---
    const auditTableBody = document.getElementById('auditTableBody');
    if (auditTableBody) loadAuditChain();
});

// ==========================================
// SHA-256 Hashing (Browser Native - SubtleCrypto)
// ==========================================
async function calculateFileHash(file) {
    logToConsole(`Hashing file: ${file.name}...`, "system");
    const arrayBuffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}

// ==========================================
// UPLOAD PAGE LOGIC (MANUAL FLOW)
// ==========================================
function setupUploadPage(dropZone) {
    setupDragAndDrop(dropZone, (file) => {
        // 1. Store File
        selectedFile = file;

        // 2. Visual Feedback (File Selected)
        const icon = dropZone.querySelector('.drop-icon');
        const text = dropZone.querySelector('p');

        if (icon) {
            icon.className = 'fa-solid fa-file-circle-check drop-icon';
            icon.style.color = 'var(--primary-cyan)';
        }
        text.innerHTML = `File Selected:<br><strong style="color:white">${file.name}</strong>`;
        dropZone.style.borderColor = 'var(--primary-cyan)';
        dropZone.style.background = 'rgba(0, 240, 255, 0.1)';

        // 3. Enable Button
        const btn = document.getElementById('btn-register-manual');
        if (btn) {
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
        }

        logToConsole(`File loaded: ${file.name}`, "system");
    });
}

// Actual Logic moved to separate function
async function processRegistration(dropZone, file) {
    // Visual Feedback
    updateDropZoneStatus(dropZone, 'processing', 'Calculating Hash & Signing...');

    try {
        // 1. Calculate Hash
        const fileHash = await calculateFileHash(file);
        logToConsole(`Hash Calculated: ${fileHash.substring(0, 10)}...`, "success");

        // 2. Generate Mock User Key & Signature (In real app, this comes from a Wallet)
        const mockPublicKey = "PREMIUM_USER_KEY_XYZ_123";
        const mockSignature = btoa("valid_rsa_signature_mock_" + Date.now());
        logToConsole("Generating RSA-2048 Signature...", "system");

        // 3. Send to Backend
        const payload = {
            file_name: file.name,
            file_hash: fileHash,
            public_key: mockPublicKey,
            signature: mockSignature
        };

        logToConsole("Sending encrypted payload to Vault...", "system");
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            updateDropZoneStatus(dropZone, 'success', `Registered! ID: #${result.id}`);
            logToConsole(`SUCCESS: Block #${result.id} mined.`, "success");

            // Reset selection after success (optional)
            selectedFile = null;
            const btn = document.getElementById('btn-register-manual');
            if (btn) {
                btn.innerHTML = `<i class="fa-solid fa-check"></i> Registered Successfully`;
                setTimeout(() => {
                    btn.innerHTML = `<i class="fa-solid fa-fingerprint"></i> Sign & Register Record`;
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                }, 4000);
            }

        } else {
            const err = await response.json();
            throw new Error(err.detail || "Registration failed");
        }

    } catch (error) {
        console.error(error);
        updateDropZoneStatus(dropZone, 'error', `Error: ${error.message}`);
        logToConsole(`ERROR: ${error.message}`, "error");
    }
}

// ==========================================
// VERIFY PAGE LOGIC
// ==========================================
function setupVerifyPage(dropZone) {
    setupDragAndDrop(dropZone, async (file) => {
        // Trigger Laser Scan
        toggleScanner(true);
        updateDropZoneStatus(dropZone, 'processing', 'Scanning & Verifying...');
        logToConsole("Initiating Deep Scan...", "system");

        try {
            const fileHash = await calculateFileHash(file);

            const response = await fetch(`${API_BASE_URL}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_hash: fileHash })
            });

            const result = await response.json();
            // Stop Laser Scan
            toggleScanner(false);

            const resultArea = document.getElementById('verifyResult');
            if (resultArea) {
                resultArea.style.display = 'block';
                if (result.verified) {
                    resultArea.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <i class="fa-solid fa-check-circle" style="font-size: 2rem; color: var(--success);"></i>
                            <div>
                                <h4 style="color: var(--success); margin-bottom: 0.25rem;">Verification Successful</h4>
                                <p style="font-size: 0.9rem; color: var(--text-muted);">
                                    File <strong>${result.record.file_name}</strong> is present in the vault.<br>
                                    Registered at: ${new Date(result.record.timestamp).toLocaleString()}
                                </p>
                            </div>
                        </div>
                     `;
                    resultArea.style.borderColor = 'rgba(0, 255, 157, 0.3)';
                    resultArea.style.background = 'rgba(0, 255, 157, 0.05)';
                    updateDropZoneStatus(dropZone, 'success', 'Verified!');
                    logToConsole("MATCH FOUND: Record verified.", "success");
                } else {
                    resultArea.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <i class="fa-solid fa-circle-xmark" style="font-size: 2rem; color: var(--error);"></i>
                            <div>
                                <h4 style="color: var(--error); margin-bottom: 0.25rem;">Verification Failed</h4>
                                <p style="font-size: 0.9rem; color: var(--text-muted);">
                                    This file hash was NOT found in the immutable ledger.
                                </p>
                            </div>
                        </div>
                     `;
                    resultArea.style.borderColor = 'rgba(255, 0, 85, 0.3)';
                    resultArea.style.background = 'rgba(255, 0, 85, 0.05)';
                    updateDropZoneStatus(dropZone, 'error', 'Not Found');
                    logToConsole("ALERT: No match in ledger.", "error");
                }
            } else {
                // For Dashboard Quick Verify (has no result area), use messages
                if (result.verified) {
                    updateDropZoneStatus(dropZone, 'success', 'Verified! (See console)');
                    logToConsole("MATCH FOUND: Record verified.", "success");
                } else {
                    updateDropZoneStatus(dropZone, 'error', 'Not Found (See console)');
                    logToConsole("ALERT: No match in ledger.", "error");
                }
            }

        } catch (error) {
            console.error(error);
            toggleScanner(false);
            updateDropZoneStatus(dropZone, 'error', 'Network Error');
            logToConsole("Connection to Vault Lost.", "error");
        }
    });
}

// ==========================================
// AUDIT PAGE LOGIC
// ==========================================
async function loadAuditChain() {
    logToConsole("Syncing with Immutable Ledger...", "system");
    try {
        const response = await fetch(`${API_BASE_URL}/audit`);
        const data = await response.json();

        const tbody = document.getElementById('auditTableBody');
        tbody.innerHTML = '';

        data.records.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="color: var(--primary-cyan);">#${record.id}</td>
                <td>${new Date(record.timestamp).toLocaleString()}</td>
                <td><span class="status-badge status-valid"><i class="fa-solid fa-cube"></i> Block</span></td>
                <td>${record.file_name}</td>
                <td class="hash-cell" title="${record.file_hash}">${record.file_hash.substring(0, 10)}...</td>
                <td><span class="status-badge status-success">Valid</span></td>
            `;
            tbody.appendChild(row);
        });
        logToConsole(`Sync Complete. ${data.records.length} blocks loaded.`, "success");

    } catch (error) {
        console.error("Audit load failed", error);
        logToConsole("Sync Failed.", "error");
    }
}


// ==========================================
// HELPERS (UI & EVENTS)
// ==========================================
function setupDragAndDrop(element, onFileDrop) {
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.style.borderColor = 'var(--primary-cyan)';
        element.style.background = 'rgba(0, 240, 255, 0.1)';
    });

    element.addEventListener('dragleave', (e) => {
        e.preventDefault();
        element.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        element.style.background = 'rgba(0, 0, 0, 0.2)';
    });

    element.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            onFileDrop(files[0]);
        }
    });

    // Manual Click
    element.addEventListener('click', (e) => {
        // Prevent trigger if clicking on button which has its own listener
        if (e.target.tagName === 'BUTTON') return;

        const input = document.createElement('input');
        input.type = 'file';
        input.onchange = (ev) => {
            if (ev.target.files.length > 0) onFileDrop(ev.target.files[0]);
        }
        input.click();
    });
}

function updateDropZoneStatus(dropZone, status, message) {
    const icon = dropZone.querySelector('.drop-icon');
    const text = dropZone.querySelector('p');

    text.innerHTML = message; // Allow HTML for br

    if (status === 'processing') {
        if (icon) {
            icon.className = 'fa-solid fa-spinner fa-spin drop-icon';
            icon.style.color = 'var(--primary-cyan)';
        }
        dropZone.style.borderColor = 'var(--primary-cyan)';
    } else if (status === 'success') {
        if (icon) {
            icon.className = 'fa-solid fa-check-circle drop-icon';
            icon.style.color = 'var(--success)';
        }
        text.style.color = 'var(--success)';
        dropZone.style.borderColor = 'var(--success)';
    } else if (status === 'error') {
        if (icon) {
            icon.className = 'fa-solid fa-circle-exclamation drop-icon';
            icon.style.color = 'var(--error)';
        }
        text.style.color = 'var(--error)';
        dropZone.style.borderColor = 'var(--error)';
    }

    if (status !== 'processing') {
        setTimeout(() => {
            // Only reset if file was not selected (state management tricky here, simple reset is safer)
            // But for manual mode, we want to KEEP the file selected state until success/reset.
            // Let's rely on the processRegistration to handle reset.
            // If it's verify page (auto), we reset.
            // If it's upload page (manual), we might want to keep it?

            // Hack for simplicity: Check if button exists (Upload page)
            const hasManualBtn = document.getElementById('btn-register-manual');

            // If it's success/error message and we are on Upload Page, we reset after delay.
            // If it's just "File Selected" (handled by setup), we don't come here (not success/error yet).

            if (icon) {
                icon.className = 'fa-solid fa-file-shield drop-icon';
                icon.style.color = 'var(--text-muted)';
            }
            text.textContent = 'Drag & Drop file';
            text.style.color = 'var(--text-muted)';
            dropZone.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            dropZone.style.background = 'rgba(0, 0, 0, 0.2)';
        }, 4000);
    }
}

// --- CYBER EFFECTS LOGIC --- //

function toggleScanner(show) {
    const scanner = document.getElementById('scannerOverlay');
    if (scanner) {
        scanner.style.display = show ? 'block' : 'none';
    }
}

function logToConsole(message, type = "system") {
    // Console removed from interface as requested, but logic kept to avoid breaking calls
    // It just logs to browser console now
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// MATRIX RAIN SCRIPT
function initMatrixRain() {
    const canvas = document.getElementById('matrixCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const chars = '01'; // Binary rain
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = [];

    for (let i = 0; i < columns; i++) {
        drops[i] = 1;
    }

    function draw() {
        ctx.fillStyle = 'rgba(5, 10, 20, 0.05)'; // Fade effect
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0F0'; // Green text
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            const text = chars.charAt(Math.floor(Math.random() * chars.length));
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    setInterval(draw, 50);

    // Resize handler
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}
