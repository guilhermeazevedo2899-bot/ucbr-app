const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('seletor', {
  aoReceber: cb => ipcRenderer.on('seletor:lista', (_e, l) => cb(l)),
  fim: v => ipcRenderer.send('seletor:fim', v),
});
