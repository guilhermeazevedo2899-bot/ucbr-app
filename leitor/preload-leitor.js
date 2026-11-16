const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('kfPonte', {
  aoFonte: cb => ipcRenderer.on('kf:fonte', (_e, f) => cb(f)),
  kill: ev => ipcRenderer.send('kf:kill', ev),
  status: s => ipcRenderer.send('kf:status', s),
});
