// Gera o instalador. Com GH_OWNER=<usuario-do-github> o app já sai com atualização automática
// pelos Releases do repositório <usuario>/ucbr-app (repositório público só com os instaladores).
const builder = require('electron-builder');
const pk = require('../package.json');
const owner = process.env.GH_OWNER, repo = process.env.GH_REPO || 'ucbr-app';
const config = { ...pk.build };
if (owner) config.publish = [{ provider: 'github', owner, repo, releaseType: 'release' }];
// No GitHub Actions (CI) já publica a release com o GITHUB_TOKEN do próprio repositório.
const publicar = process.env.CI && owner ? 'always' : 'never';
builder.build({ targets: builder.Platform.WINDOWS.createTarget('nsis', builder.Arch.x64), config, publish: publicar })
  .then(f => console.log('pronto:', f.join('\n'), owner ? `\natualização automática: github.com/${owner}/${repo}` : '\n(sem atualização automática: defina GH_OWNER)'))
  .catch(e => { console.error(e); process.exit(1); });
