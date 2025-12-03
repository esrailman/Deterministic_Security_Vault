function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('message');

    if (fileInput.files.length === 0) {
        message.innerText = "Please select a file first.";
        return;
    }

    message.innerText = "Uploading...";
    
    // Mock upload process
    setTimeout(() => {
        window.location.href = 'verify.html';
    }, 1000);
}
