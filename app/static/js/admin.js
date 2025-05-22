document.getElementById('tracking-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/admin', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) throw new Error('Failed to generate QR code.');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Filename logic from server response (or fallback)
        a.download = 'qr_code.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        console.error('Error:', err);
        alert('QR code generation failed.');
    }
});
