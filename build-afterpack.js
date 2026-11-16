// Coloca o ícone do clã e os dados (nome, versão, autor) dentro do U.C.B.R.exe.
// Feito em JS puro (resedit) para gerar o .exe sem precisar de Windows nem Wine.
const fs = require('fs');
const path = require('path');

exports.default = async function (ctx) {
  if (ctx.electronPlatformName !== 'win32') return;
  const ResEdit = await import('resedit');
  const R = ResEdit.default || ResEdit;
  const { productFilename } = ctx.packager.appInfo;
  const versao = ctx.packager.appInfo.version;
  const exe = path.join(ctx.appOutDir, `${productFilename}.exe`);
  const bin = R.NtExecutable.from(fs.readFileSync(exe), { ignoreCert: true });
  const res = R.NtExecutableResource.from(bin);

  const ico = R.Data.IconFile.from(fs.readFileSync(path.join(__dirname, 'build', 'icon.ico')));
  const grupos = R.Resource.IconGroupEntry.fromEntries(res.entries);
  const id = grupos.length ? grupos[0].id : 1, lang = grupos.length ? grupos[0].lang : 1033;
  R.Resource.IconGroupEntry.replaceIconsForResource(res.entries, id, lang, ico.icons.map(i => i.data));

  const vi = R.Resource.VersionInfo.fromEntries(res.entries)[0] || R.Resource.VersionInfo.createEmpty();
  const [a, b, c] = versao.split('.').map(n => parseInt(n, 10) || 0);
  vi.setFileVersion(a, b, c, 0, 1033); vi.setProductVersion(a, b, c, 0, 1033);
  const lng = vi.getAllLanguagesForStringValues()[0] || { lang: 1033, codepage: 1200 };
  vi.setStringValues(lng, {
    FileDescription: 'U.C.B.R', ProductName: 'U.C.B.R', CompanyName: 'Clã U.C.B.R',
    LegalCopyright: 'Guilherme Azevedo', OriginalFilename: `${productFilename}.exe`, InternalName: 'ucbr',
    FileVersion: versao, ProductVersion: versao,
  });
  vi.outputToResourceEntries(res.entries);

  res.outputResource(bin);
  fs.writeFileSync(exe, Buffer.from(bin.generate()));
  console.log('  • ícone e versão gravados em', path.basename(exe));
};
