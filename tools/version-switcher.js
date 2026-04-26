#!/usr/bin/env node
/**
 * Generic version switcher — run from a git repo root that has a versions.json.
 *
 * versions.json format:
 * {
 *   "port": 3003,
 *   "serve": "path/to/app.html",       // file to inject version bar into
 *   "assets": ["path/to/data.js"],     // other files to serve (by filename at /<basename>)
 *   "versions": [
 *     { "label": "v1 — Description", "hash": "abc1234" },
 *     ...
 *   ]
 * }
 */

const http = require('http');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const repoRoot = process.cwd();
const configArg = process.argv[2];
const configPath = configArg
  ? path.resolve(repoRoot, configArg)
  : path.join(repoRoot, 'versions.json');

if (!fs.existsSync(configPath)) {
  console.error('No versions.json found. Pass a path: node version-switcher.js tools/transcript-cutter/versions.json');
  process.exit(1);
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
const configDir = path.dirname(configPath);
const { port = 3003, serve, assets = [], versions } = config;

// Resolve paths relative to the versions.json location
const resolvedServe = path.relative(repoRoot, path.resolve(configDir, serve));
const resolvedAssets = assets.map(a => path.relative(repoRoot, path.resolve(configDir, a)));

if (!serve || !versions?.length) {
  console.error('versions.json must include "serve" (path to HTML file) and "versions" (array of {label, hash})');
  process.exit(1);
}

const appFile = path.join(repoRoot, resolvedServe);
let active = versions[versions.length - 1].hash;

function switchTo(hash) {
  if (!/^[0-9a-f]{7,40}$|^HEAD$/.test(hash)) return false;
  execSync(`git checkout ${hash} -- ${resolvedServe}`, { cwd: repoRoot });
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

function versionBarHTML(active) {
  return `
<div id="version-bar">
  <span>versions:</span>
  ${versions.map(v => `
  <form method="POST" action="/switch">
    <input type="hidden" name="hash" value="${v.hash}" />
    <button type="submit" ${active === v.hash ? 'class="active"' : ''}>${v.label}</button>
  </form>`).join('')}
</div>`;
}

function serveApp(res) {
  let html = fs.readFileSync(appFile, 'utf8');
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

  // Serve declared assets by their basename (e.g. transcript-cutter/data.js → /data.js)
  for (const assetPath of resolvedAssets) {
    if (req.url === '/' + path.basename(assetPath)) {
      const full = path.join(repoRoot, assetPath);
      if (fs.existsSync(full)) {
        res.writeHead(200, { 'Content-Type': 'application/javascript' });
        res.end(fs.readFileSync(full));
      } else {
        res.writeHead(404);
        res.end('// not found: ' + assetPath);
      }
      return;
    }
  }

  serveApp(res);
});

server.listen(port, () => {
  console.log(`Version switcher → http://localhost:${port}`);
  console.log(`Serving          → ${appFile}`);
});
