(async function () {
  try {
    const res = await fetch('/parts.json');
    if (!res.ok) return;
    const parts = await res.json();

    const style = document.createElement('style');
    style.textContent = `
      #part-bar {
        position: fixed;
        top: 12px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
        display: flex;
        gap: 6px;
        padding: 5px;
        background: rgba(5, 6, 18, 0.78);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 225, 53, 0.18);
        border-radius: 999px;
        transition: opacity .25s ease, transform .25s ease;
      }
      body.hide-ui #part-bar {
        opacity: 0;
        pointer-events: none;
        transform: translate(-50%, -120%);
      }
      .part-link {
        padding: 6px 14px;
        border-radius: 999px;
        font-family: 'Nunito', sans-serif;
        font-size: 12px;
        font-weight: 900;
        text-decoration: none;
        color: #7B849E;
        transition: color .15s, background .15s;
        white-space: nowrap;
      }
      .part-link:hover {
        color: #EEF0FA;
        background: rgba(255, 255, 255, 0.08);
      }
      .part-link.active {
        background: #FFE135;
        color: #050612;
        box-shadow: 0 0 16px rgba(255, 225, 53, 0.35);
      }
    `;
    document.head.appendChild(style);

    const normalize = (p) => p.replace(/\/index\.html$/, '').replace(/\/+$/, '') || '/';
    const current = normalize(window.location.pathname);

    const bar = document.createElement('nav');
    bar.id = 'part-bar';
    bar.setAttribute('aria-label', 'Series Parts');

    parts.forEach((part) => {
      const a = document.createElement('a');
      a.href = part.path;
      a.textContent = part.label;
      a.className = 'part-link' + (normalize(part.path) === current ? ' active' : '');
      bar.appendChild(a);
    });

    document.body.appendChild(bar);
  } catch (err) {
    console.error('Could not load parts navigation:', err);
  }
})();
