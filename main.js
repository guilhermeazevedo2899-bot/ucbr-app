// U.C.B.R — app para Windows (Electron)
// Abre a plataforma (ucbr.pages.dev) numa janela própria e adiciona o que o navegador não faz:
// push-to-talk global, bandeja, iniciar com o Windows, avisos do Windows e escolha de janela/tela.
const { app, protocol, net, powerMonitor, BrowserWindow, Tray, Menu, ipcMain, session, desktopCapturer, shell, nativeImage, Notification, nativeTheme, dialog } = require('electron');
const path = require('path');
const fs = require('fs');

const APP_URL = 'https://ucbr.pages.dev/';
// O app leva a plataforma inteira dentro dele (pasta site/). Os pedidos para ucbr.pages.dev
// são respondidos daqui mesmo, sem internet e sem o site precisar estar no ar.
// O endereço continua o mesmo, então login, convites, YouTube e o banco funcionam igual.
const SITE = path.join(__dirname, 'site');
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.wasm': 'application/wasm', '.pdf': 'application/pdf', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.txt': 'text/plain; charset=utf-8', '.bin': 'application/octet-stream' };
const ORIGEM = new URL(APP_URL).origin;
// Sites que abrem dentro do app (login e banco). O resto abre no navegador.
const DENTRO = [ORIGEM, 'https://baiydznqcfsvnqbfvjzz.supabase.co'];

app.setAppUserModelId('br.ucbr.app');
nativeTheme.themeSource = 'dark';
// Áudio e vídeo continuam rodando com a janela escondida ou atrás do jogo
app.commandLine.appendSwitch('disable-background-timer-throttling');
app.commandLine.appendSwitch('disable-renderer-backgrounding');
app.commandLine.appendSwitch('disable-backgrounding-occluded-windows');

if (!app.requestSingleInstanceLock()) { app.quit(); process.exit(0); }

/* ----------------------------- configurações ----------------------------- */
const CFG_ARQ = () => path.join(app.getPath('userData'), 'config-app.json');
const PADRAO = {
  ptt: false,                // apertar para falar
  pttTecla: null,            // { tipo: 'tecla'|'mouse', code, nome }
  pttSom: true,              // bipe ao apertar/soltar
  pttSoltar: 200,            // ms depois de soltar a tecla (não corta o fim da palavra)
  muteTecla: null,           // liga/desliga microfone
  deafTecla: null,           // liga/desliga fone
  avisoMsg: true,            // aviso do Windows para mensagem nova
  avisoSala: true,           // aviso quando alguém entra numa sala de voz
  fecharBandeja: true,       // X esconde perto do relógio
  iniciarComWindows: true,
  iniciarEscondido: true,
};
let CFG = { ...PADRAO };
try { CFG = { ...PADRAO, ...JSON.parse(fs.readFileSync(CFG_ARQ(), 'utf8')) }; } catch {}
// Grava num arquivo temporário e troca de nome: se o PC desligar no meio, o arquivo antigo fica inteiro.
function salvarCfg() { try { const t = CFG_ARQ() + '.tmp'; fs.writeFileSync(t, JSON.stringify(CFG, null, 2)); fs.renameSync(t, CFG_ARQ()); } catch (e) { log('config', e); } }
// Registro simples de erros (para descobrir o que houve no PC de alguém): %APPDATA%/U.C.B.R/registro.txt
function log(...a) {
  try {
    const arq = path.join(app.getPath('userData'), 'registro.txt');
    try { if (fs.statSync(arq).size > 512 * 1024) fs.renameSync(arq, arq + '.antigo'); } catch {}
    fs.appendFileSync(arq, `[${new Date().toISOString()}] ` + a.map(x => x instanceof Error ? x.stack || x.message : typeof x === 'string' ? x : JSON.stringify(x)).join(' ') + '\n');
  } catch {}
}
process.on('uncaughtException', e => log('erro', e));
process.on('unhandledRejection', e => log('promessa', e));

function aplicarInicio() {
  if (!app.isPackaged) return;
  app.setLoginItemSettings({ openAtLogin: !!CFG.iniciarComWindows, args: CFG.iniciarEscondido ? ['--escondido'] : [] });
}

/* --------------------------------- janela -------------------------------- */
let win = null, tray = null, saindo = false, avisouBandeja = false, naoLidas = 0;
const ICONE = path.join(__dirname, 'build', 'icon.png');
const ICONE_ICO = path.join(__dirname, 'build', 'icon.ico');

function criarJanela() {
  const escondido = process.argv.includes('--escondido') && !linkUcbr(process.argv);
  win = new BrowserWindow({
    width: 1400, height: 880, minWidth: 900, minHeight: 600,
    backgroundColor: '#0b0b0d', show: false, title: 'U.C.B.R',
    icon: fs.existsSync(ICONE_ICO) ? ICONE_ICO : ICONE,
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, sandbox: false,
      backgroundThrottling: false, spellcheck: true,
    },
  });
  win.setMenu(null);
  const h = linkUcbr(process.argv);
  win.loadURL(APP_URL + (h ? '#' + h : ''));
  win.once('ready-to-show', () => { if (!escondido) win.show(); });

  // Sem internet ou site fora do ar: tela própria que tenta de novo sozinha
  win.webContents.on('did-fail-load', (_e, code, _d, url, principal) => {
    if (!principal || code === -3) return; // -3 = navegação cancelada
    win.loadFile(path.join(__dirname, 'offline.html'), { query: { u: url || APP_URL } });
  });

  // Links de fora (YouTube, WhatsApp, Gartic...) abrem no navegador normal
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (DENTRO.some(o => url.startsWith(o))) return { action: 'allow' };
    if (/^https?:|^mailto:/.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  win.webContents.on('will-navigate', (e, url) => {
    if (url.startsWith('file:') || DENTRO.some(o => url.startsWith(o))) return;
    e.preventDefault(); if (/^https?:/.test(url)) shell.openExternal(url);
  });

  win.on('close', e => {
    if (saindo || !CFG.fecharBandeja) return;
    e.preventDefault(); win.hide();
    if (!avisouBandeja && tray) {
      avisouBandeja = true;
      try { tray.displayBalloon({ iconType: 'info', title: 'U.C.B.R continua ligado', content: 'A voz segue funcionando. Clique no ícone perto do relógio para abrir. Para fechar de vez: botão direito > Sair.' }); } catch {}
    }
  });
  win.on('focus', () => { win.flashFrame(false); });
  // Se a página travar ou fechar sozinha, recarrega em vez de ficar tela preta
  win.webContents.on('render-process-gone', (_e, d) => { log('pagina caiu', d); if (d.reason !== 'clean-exit') setTimeout(() => win?.loadURL(APP_URL), 1000); });
  win.webContents.on('unresponsive', () => log('pagina sem responder'));
}

function mostrar() {
  if (!win) return;
  if (win.isMinimized()) win.restore();
  win.show(); win.focus();
}

function montarBandeja() {
  tray = new Tray(nativeImage.createFromPath(fs.existsSync(ICONE_ICO) ? ICONE_ICO : ICONE));
  tray.setToolTip('U.C.B.R');
  tray.on('click', mostrar);
  atualizarMenu();
}
function atualizarMenu() {
  if (!tray) return;
  tray.setContextMenu(Menu.buildFromTemplate([
    { label: 'Abrir U.C.B.R', click: mostrar },
    { type: 'separator' },
    { label: 'Microfone: ligar/desligar', click: () => enviar('atalho', 'mute') },
    { label: 'Fone: ligar/desligar', click: () => enviar('atalho', 'deaf') },
    { label: 'Configurações do app (atalhos)', click: () => { mostrar(); enviar('abrirConfig'); } },
    { type: 'separator' },
    { label: 'Iniciar junto com o Windows', type: 'checkbox', checked: !!CFG.iniciarComWindows, click: m => { CFG.iniciarComWindows = m.checked; salvarCfg(); aplicarInicio(); } },
    { label: 'Procurar atualização', click: () => procurarAtualizacao(true) },
    { label: 'Recarregar', click: () => { win?.loadURL(APP_URL); } },
    { type: 'separator' },
    { label: `Versão do app ${app.getVersion()}`, enabled: false },
    { label: 'Sair', click: () => { saindo = true; app.quit(); } },
  ]));
}

function enviar(canal, ...a) { try { win?.webContents.send(canal, ...a); } catch {} }

/* ------------------------- permissões e compartilhar tela ------------------------- */
function servirLocal(req) {
  const u = new URL(req.url);
  let rel = decodeURIComponent(u.pathname);
  if (rel.endsWith('/')) rel += 'index.html';
  const arq = path.normalize(path.join(SITE, rel));
  if (!arq.startsWith(SITE + path.sep)) return new Response('Proibido', { status: 403 });
  try {
    const dados = fs.readFileSync(arq);
    return new Response(dados, { status: 200, headers: { 'content-type': TIPOS[path.extname(arq).toLowerCase()] || 'application/octet-stream', 'cache-control': 'no-cache', 'access-control-allow-origin': '*' } });
  } catch { return new Response('Não encontrado', { status: 404, headers: { 'content-type': 'text/plain; charset=utf-8' } }); }
}
function configurarSessao() {
  const s = session.defaultSession;
  const HOST = new URL(APP_URL).host;
  s.protocol.handle('https', req => {
    try { if (new URL(req.url).host === HOST) return servirLocal(req); } catch {}
    return net.fetch(req, { bypassCustomProtocolHandlers: true });
  });
  const nossa = url => { try { return DENTRO.includes(new URL(url).origin) || url.startsWith('file:'); } catch { return false; } };
  s.setPermissionRequestHandler((wc, perm, cb, det) => {
    const ok = ['media', 'notifications', 'clipboard-read', 'clipboard-sanitized-write', 'fullscreen', 'display-capture', 'speaker-selection', 'idle-detection', 'pointerLock'].includes(perm);
    cb(ok && nossa(det.requestingUrl || wc.getURL()));
  });
  s.setPermissionCheckHandler((_wc, _perm, origem) => nossa(origem || ''));

  // Botão "Transmitir tela": mostra janelas abertas (ex.: DayZ) e telas inteiras com miniatura
  s.setDisplayMediaRequestHandler(async (_req, cb) => {
    try {
      const fontes = await desktopCapturer.getSources({ types: ['window', 'screen'], thumbnailSize: { width: 320, height: 180 }, fetchWindowIcons: true });
      const lista = fontes.filter(f => f.name && !/^U\.C\.B\.R/.test(f.name) || f.id.startsWith('screen'))
        .map(f => ({ id: f.id, nome: f.name, tela: f.id.startsWith('screen'), img: f.thumbnail.toDataURL(), ico: f.appIcon ? f.appIcon.toDataURL() : '' }));
      const escolha = await abrirSeletor(lista);
      const fonte = escolha && fontes.find(f => f.id === escolha.id);
      if (!fonte) return cb({});
      // Áudio do PC (loopback) só existe no Windows; vai junto quando o membro marca "com som"
      cb(escolha.som && process.platform === 'win32' ? { video: fonte, audio: 'loopback' } : { video: fonte });
    } catch (e) { log('tela', e); cb({}); }
  }, { useSystemPicker: false });
}

let seletor = null;
function abrirSeletor(lista) {
  return new Promise(res => {
    if (seletor) { try { seletor.close(); } catch {} }
    seletor = new BrowserWindow({
      parent: win, modal: true, width: 900, height: 640, resizable: false, minimizable: false, maximizable: false,
      backgroundColor: '#0b0b0d', title: 'Transmitir tela', autoHideMenuBar: true, show: false,
      icon: fs.existsSync(ICONE_ICO) ? ICONE_ICO : ICONE,
      webPreferences: { preload: path.join(__dirname, 'preload-seletor.js'), contextIsolation: true },
    });
    seletor.setMenu(null);
    let feito = false;
    const fim = v => { if (feito) return; feito = true; ipcMain.removeAllListeners('seletor:fim'); try { seletor?.close(); } catch {} seletor = null; res(v); };
    ipcMain.once('seletor:fim', (_e, v) => fim(v));
    seletor.on('closed', () => fim(null));
    seletor.loadFile(path.join(__dirname, 'seletor.html'));
    seletor.webContents.once('did-finish-load', () => { seletor?.webContents.send('seletor:lista', lista); seletor?.show(); });
  });
}

/* --------------------------- atalhos globais (PTT) --------------------------- */
// uiohook escuta teclado e mouse mesmo com o DayZ em primeiro plano (como o Discord faz).
let hook = null, capturando = null;
const apertadas = new Set();
const nomeTecla = {};
function iniciarHook() {
  try {
    const { uIOhook, UiohookKey } = require('uiohook-napi');
    for (const [n, c] of Object.entries(UiohookKey)) if (!nomeTecla[c]) nomeTecla[c] = n;
    const igual = (t, tipo, code) => t && t.tipo === tipo && t.code === code;
    // Segurança do push-to-talk: o Windows repete o "apertou" enquanto a tecla está segurada.
    // Se o "soltou" se perder (ex.: Alt+Tab, tela de bloqueio), o microfone fecha sozinho em 1,5 s.
    let vigia = null;
    const soltarTudo = () => { apertadas.clear(); enviar('ptt', false); };
    const evento = (tipo, code, desceu) => {
      const k = tipo + ':' + code;
      if (tipo === 'tecla' && CFG.ptt && igual(CFG.pttTecla, tipo, code)) {
        clearTimeout(vigia);
        if (desceu) vigia = setTimeout(() => { if (apertadas.has(k)) { apertadas.delete(k); enviar('ptt', false); } }, 1500);
      }
      if (desceu) { if (apertadas.has(k)) return; apertadas.add(k); } else apertadas.delete(k);
      if (capturando && desceu) {
        if (tipo === 'mouse' && code <= 2) return; // botão esquerdo/direito não servem de atalho
        const nome = tipo === 'mouse' ? `Botão ${code} do mouse` : (nomeTecla[code] || `Tecla ${code}`);
        const c = capturando; capturando = null;
        return c({ tipo, code, nome: tipo === 'tecla' && code === 1 ? null : nome }); // Esc = apagar atalho
      }
      if (CFG.ptt && igual(CFG.pttTecla, tipo, code)) enviar('ptt', desceu);
      if (desceu && igual(CFG.muteTecla, tipo, code)) enviar('atalho', 'mute');
      if (desceu && igual(CFG.deafTecla, tipo, code)) enviar('atalho', 'deaf');
    };
    uIOhook.on('keydown', e => evento('tecla', e.keycode, true));
    uIOhook.on('keyup', e => evento('tecla', e.keycode, false));
    uIOhook.on('mousedown', e => evento('mouse', e.button, true));
    uIOhook.on('mouseup', e => evento('mouse', e.button, false));
    uIOhook.start();
    hook = uIOhook;
    powerMonitor.on('lock-screen', soltarTudo);
    powerMonitor.on('suspend', soltarTudo);
  } catch (e) { log('Atalho global indisponível', e); }
}

/* ------------------------------ ponte com o site ------------------------------ */
ipcMain.handle('desk:info', () => ({ versao: app.getVersion(), hook: !!hook, cfg: CFG }));
ipcMain.handle('desk:salvar', (_e, novo) => {
  const ok = Object.keys(PADRAO);
  for (const k of ok) if (k in (novo || {})) CFG[k] = novo[k];
  salvarCfg(); aplicarInicio(); atualizarMenu();
  return CFG;
});
ipcMain.handle('desk:capturar', () => new Promise(res => {
  if (!hook) return res(null);
  if (capturando) capturando(null);
  capturando = res;
  setTimeout(() => { if (capturando === res) { capturando = null; res(undefined); } }, 15000);
}));
ipcMain.on('desk:mostrar', mostrar);
ipcMain.on('desk:badge', (_e, n) => {
  naoLidas = Math.max(0, n | 0);
  if (!win) return;
  try { tray?.setToolTip(naoLidas ? `U.C.B.R • ${naoLidas} nova(s)` : 'U.C.B.R'); } catch {}
  if (naoLidas && !win.isFocused()) win.flashFrame(true);
});
// Aviso do Windows feito aqui (clicar abre a janela mesmo escondida na bandeja)
ipcMain.on('desk:aviso', (_e, a) => {
  if (!Notification.isSupported() || !a?.titulo) return;
  const n = new Notification({ title: String(a.titulo).slice(0, 120), body: String(a.corpo || '').slice(0, 200), icon: fs.existsSync(ICONE) ? ICONE : undefined, silent: !!a.mudo });
  n.on('click', () => { mostrar(); if (a.abrir) enviar('abrirAviso', a.abrir); });
  n.show();
});

/* --------------------------------- atualizações -------------------------------- */
let updater = null;
function procurarAtualizacao(manual) {
  if (!app.isPackaged) { if (manual) dialog.showMessageBox({ message: 'Atualização só funciona no app instalado.' }); return; }
  // Só procura se o instalador foi gerado com o endereço do GitHub do clã (arquivo app-update.yml)
  if (!fs.existsSync(path.join(process.resourcesPath, 'app-update.yml'))) {
    if (manual) dialog.showMessageBox(win, { message: 'Atualização automática ainda não configurada.', detail: 'Baixe a versão nova pelo link do clã e instale por cima. Nada se perde.' });
    return;
  }
  try {
    if (!updater) {
      updater = require('electron-updater').autoUpdater;
      updater.autoDownload = true; updater.autoInstallOnAppQuit = true;
      updater.on('update-downloaded', i => {
        dialog.showMessageBox(win, { type: 'info', title: 'U.C.B.R', message: `Versão ${i.version} do app baixada.`, detail: 'Reiniciar agora para instalar?', buttons: ['Reiniciar agora', 'Depois'], defaultId: 0 })
          .then(r => { if (r.response === 0) { saindo = true; updater.quitAndInstall(true, true); } });
      });
      updater.on('error', e => { if (updater._manual) dialog.showMessageBox(win, { type: 'warning', message: 'Não consegui procurar atualização agora.', detail: String(e?.message || e).slice(0, 300) }); updater._manual = false; });
      updater.on('update-not-available', () => { if (updater._manual) dialog.showMessageBox(win, { message: 'Você já está com a versão mais nova do app.' }); updater._manual = false; });
    }
    updater._manual = !!manual;
    updater.checkForUpdates().catch(() => {});
  } catch (e) { log('atualizacao', e); }
}

/* ------------------------- links ucbr:// (convite, nova senha) ------------------------- */
// A página de download do clã repassa #convite=... e o link de nova senha para ucbr://abrir#...
function linkUcbr(argv) {
  const a = (argv || []).find(x => /^ucbr:\/\//i.test(x));
  if (!a) return null;
  const i = a.indexOf('#'); if (i < 0) return '';
  const h = a.slice(i + 1);
  return /^[A-Za-z0-9_\-=&.%~+]{1,4000}$/.test(h) ? h : '';
}
function abrirLink(h) {
  if (h === null || !win) return;
  mostrar();
  if (h) win.loadURL(APP_URL + '#' + h);
}
if (process.defaultApp) app.setAsDefaultProtocolClient('ucbr', process.execPath, [path.resolve(process.argv[1] || '.')]);
else app.setAsDefaultProtocolClient('ucbr');

/* ----------------------------------- início ----------------------------------- */
app.on('second-instance', (_e, argv) => { mostrar(); abrirLink(linkUcbr(argv)); });
app.whenReady().then(() => {
  configurarSessao();
  criarJanela();
  montarBandeja();
  iniciarHook();
  aplicarInicio();
  setTimeout(() => procurarAtualizacao(false), 15000);
  setInterval(() => procurarAtualizacao(false), 6 * 3600 * 1000);
});
app.on('before-quit', () => { saindo = true; try { hook?.stop(); } catch {} });
app.on('window-all-closed', () => { if (saindo) app.quit(); });
