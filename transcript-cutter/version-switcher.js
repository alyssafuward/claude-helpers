const http = require('http');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const repoRoot = path.resolve(__dirname, '..');
const appFile = path.join(__dirname, 'index.html');
const dataFile = path.join(__dirname, 'data.js');

const versions = [
  { label: 'v1 — Basic transcript viewer',            hash: 'd514a64' },
  { label: 'v2 — localStorage, cmd+click, save/load', hash: 'd491a68' },
  { label: 'v3 — Tabs, sections, boundary drag',      hash: '6302ffb' },
];

let active = '6302ffb';

function switchTo(hash) {
  if (!/^[0-9a-f]{7,40}$|^HEAD$/.test(hash)) return false;
  execSync(`git checkout ${hash} -- transcript-cutter/index.html`, { cwd: repoRoot });
  active = hash;
  return true;
}

const versionBarCSS = `
<style id="version-bar-style">
#version-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #1e293b;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-family: system-ui, sans-serif;
  font-size: 11px;
  z-index: 99999;
  border-top: 1px solid #334155;
}
#version-bar span { color: #64748b; margin-right: 4px; }
#version-bar form { display: inline; }
#version-bar button {
  background: #334155;
  border: 1px solid #475569;
  color: #cbd5e1;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  font-family: inherit;
}
#version-bar button:hover { background: #475569; }
#version-bar button.active { background: #2563eb; color: white; border-color: #2563eb; }
</style>`;

const versionBarHTML = (active) => `
<div id="version-bar">
  <span>versions:</span>
  ${versions.map(v => `
  <form method="POST" action="/switch">
    <input type="hidden" name="hash" value="${v.hash}" />
    <button type="submit" ${active === v.hash ? 'class="active"' : ''}>${v.label}</button>
  </form>`).join('')}
</div>`;

function serveApp(res) {
  let html = fs.readFileSync(appFile, 'utf8');
  // Inject version bar styles into <head> and bar before </body>
  html = html.replace('</head>', versionBarCSS + '\n</head>');
  html = html.replace('</body>', versionBarHTML(active) + '\n</body>');
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end(html);
}

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/switch') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      const hash = new URLSearchParams(body).get('hash');
      try { switchTo(hash); } catch (e) { console.error(e.message); }
      res.writeHead(302, { Location: '/' });
      res.end();
    });
    return;
  }

  // Serve data.js so the app can load transcript data
  if (req.url === '/data.js') {
    if (fs.existsSync(dataFile)) {
      res.writeHead(200, { 'Content-Type': 'application/javascript' });
      res.end(fs.readFileSync(dataFile));
    } else {
      res.writeHead(404);
      res.end('// data.js not found');
    }
    return;
  }

  serveApp(res);
});

server.listen(3003, () => {
  console.log('Transcript Cutter (with versions) → http://localhost:3003');
});
