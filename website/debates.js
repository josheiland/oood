(() => {
  const storageKey = 'oood.debate-browser';
  let browser;

  function browserId() {
    if (browser) return browser;
    try {
      const stored = localStorage.getItem(storageKey) || crypto.randomUUID();
      localStorage.setItem(storageKey, stored);
      browser = stored;
      return stored;
    } catch {
      return null;
    }
  }

  document.querySelectorAll('[data-debate]').forEach((card) => {
    const buttons = card.querySelectorAll('.side');
    const followup = card.querySelector('.debate__followup');
    let lastWrite = Promise.resolve();
    let revision = 0;

    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const selection = ++revision;
        buttons.forEach((option) => option.setAttribute('aria-pressed', String(option === button)));
        followup.textContent = button.dataset.followup;
        const id = browserId();
        if (!id) return;

        // Send changes in order so a fast switch keeps the visitor's last choice.
        lastWrite = lastWrite.then(async () => {
          if (selection !== revision) return;
          try {
            const response = await fetch('/api/debate-votes', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ debate: card.dataset.debate, choice: Number(button.dataset.option), browser: id })
            });
            if (response.ok) return;
          } catch { /* Keep the follow-up available if the tally is down. */ }
          if (selection === revision) {
            const note = document.createElement('small');
            note.textContent = 'We couldn’t count your pick this time';
            followup.appendChild(note);
          }
        });
      });
    });
  });
})();
