/**
 * Sprint 3 Mock Javascript Logic
 * Handles simple form submissions and feedback display.
 */

function handleUpload(event) {
    event.preventDefault();

    // Simulate processing
    const fileInput = document.getElementById('fileInput');
    const feedback = document.getElementById('uploadFeedback');

    if (fileInput.files.length === 0) {
        alert("Please select a file first.");
        return;
    }

    const fileName = fileInput.files[0].name;

    feedback.className = 'feedback success';
    feedback.innerHTML = `
        <h3>Upload Successful! <span class="badge badge-success">Registered</span></h3>
        <p>File <strong>${fileName}</strong> has been securely registered in the vault.</p>
        <p>Generated Hash: <code>0x${Math.random().toString(16).substr(2, 10)}...</code></p>
        <br>
        <a href="verify.html" class="btn btn-sm">Verify this file now</a>
    `;
    feedback.style.display = 'block';
}

function handleVerify(event) {
    event.preventDefault();

    const fileInput = document.getElementById('verifyFileInput');
    const hashInput = document.getElementById('hashInput');
    const feedback = document.getElementById('verifyFeedback');

    let fileName = "Unknown File";
    if (fileInput.files.length > 0) {
        fileName = fileInput.files[0].name;
    } else if (hashInput.value) {
        fileName = "Hash: " + hashInput.value;
    } else {
        alert("Please select a file or enter a hash to verify.");
        return;
    }

    // Randomize success/failure for demonstration purposes
    const isSuccess = Math.random() > 0.3; // 70% chance of success

    if (isSuccess) {
        feedback.className = 'feedback success';
        feedback.innerHTML = `
            <h3>Verification Passed <span class="badge badge-success">Valid</span></h3>
            <p>The file <strong>${fileName}</strong> matches the stored record.</p>
            <p>Integrity: <strong>100% Verified</strong></p>
            <br>
            <a href="audit.html" class="btn btn-sm">View Audit Log</a>
        `;
    } else {
        feedback.className = 'feedback error';
        feedback.innerHTML = `
            <h3>Verification Failed <span class="badge badge-error">Tampered</span></h3>
            <p>Warning! The file <strong>${fileName}</strong> does not match our records.</p>
            <p>Possible tampering detected.</p>
            <br>
            <a href="audit.html" class="btn btn-sm btn-secondary">Check Audit Log</a>
        `;
    }
    feedback.style.display = 'block';
}

function showProof(hashId) {
    alert(`Mock Proof for Hash ID: ${hashId}\n\nThis would display the Merkle Proof details in a real implementation.`);
}
