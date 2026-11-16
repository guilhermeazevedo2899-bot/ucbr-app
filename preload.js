// Ponte entre o site e o app do PC. O site só usa isso se window.ucbrDesktop existir.
const { contextBridge, ipcRenderer } = require('electron');

const ouvir = (canal, cb) => {
  const f = (_e, ...a) => { try { cb(...a); } catch (err) { console.error(err); } };
  ipcRenderer.on(canal, f);
  return () => ipcRenderer.removeListener(canal, f);
};

contextBridge.exposeInMainWorld('ucbrDesktop', {
  plataforma: process.platform,
  info: () => ipcRenderer.invoke('desk:info'),
  salvar: cfg => ipcRenderer.invoke('desk:salvar', cfg),
  capturarTecla: () => ipcRenderer.invoke('desk:capturar'),
  mostrar: () => ipcRenderer.send('desk:mostrar'),
  badge: n => ipcRenderer.send('desk:badge', n),
  aviso: a => ipcRenderer.send('desk:aviso', a),
  onPTT: cb => ouvir('ptt', cb),
  onAtalho: cb => ouvir('atalho', cb),
  onAbrirConfig: cb => ouvir('abrirConfig', cb),
  onAbrirAviso: cb => ouvir('abrirAviso', cb),
});
