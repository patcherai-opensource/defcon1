
    const form     = document.getElementById('scrapeForm');
    const input    = document.getElementById('urlInput');
    const btn      = document.getElementById('submitBtn');
    const feedback = document.getElementById('feedback');
 
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const url = input.value.trim();
      if (!url) return;
 
      btn.disabled = true;
      showFeedback('load', '<span class="spinner"></span> Downloading &amp; validating…');
 
      try {
        const formData = new FormData();
        formData.append('url', url);
 
        const res  = await fetch('/scrape', { method: 'POST', body: formData });
        const data = await res.json();
 
        if (data.success) {
          showFeedback('ok', `✓ Archived as ${data.image.file_format} (${data.image.width}×${data.image.height})`);
          input.value = '';
          // Reload after short delay to show new image in gallery
          setTimeout(() => location.reload(), 800);
        } else {
          showFeedback('err', `✗ ${data.error}`);
        }
      } catch (err) {
        showFeedback('err', `✗ Network error: ${err.message}`);
      } finally {
        btn.disabled = false;
      }
    });
 
    function showFeedback(type, html) {
      feedback.className = 'feedback ' + type;
      feedback.innerHTML = html;
    }