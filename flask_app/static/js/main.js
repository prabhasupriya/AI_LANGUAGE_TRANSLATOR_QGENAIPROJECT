document.addEventListener('DOMContentLoaded', () => {
    const inputText = document.getElementById('inputText');
    const outputText = document.getElementById('outputText');
    const translateBtn = document.getElementById('translateBtn');

    translateBtn.addEventListener('click', async () => {
        const text = inputText.value.trim();
        if (!text) return;

        // Show loading state
        document.getElementById('loadingOverlay').classList.remove('hidden');

        const response = await fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                source_lang: document.getElementById('sourceLang').value,
                target_lang: document.getElementById('targetLang').value
            })
        });

        const data = await response.json();
        document.getElementById('loadingOverlay').classList.add('hidden');
        
        if (data.success) {
            outputText.textContent = data.translated_text;
        } else {
            alert("Error: " + data.error);
        }
    });
});