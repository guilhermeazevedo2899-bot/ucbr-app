import sys, re
P = sys.argv[1]; CSS = sys.argv[2]
s = open(P, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n: raise SystemExit(f'esperava {n}x, achei {c}x: {a[:90]!r}')
    s = s.replace(a, b)

# ---------- CSS ----------
css = open(CSS, encoding='utf-8').read()
k = s.index('</style>'); s = s[:k] + css + '\n' + s[k:]

ICO_CTRL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 8h12a4 4 0 0 1 4 4v1a3 3 0 0 1-5.4 1.8L15 13H9l-1.6 1.8A3 3 0 0 1 2 13v-1a4 4 0 0 1 4-4z"/><path d="M7 11v3M5.5 12.5h3"/><circle cx="16" cy="11" r=".8" fill="currentColor"/><circle cx="18" cy="13" r=".8" fill="currentColor"/></svg>'
ICO_COR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 20h4L19 9a2.8 2.8 0 0 0-4-4L4 16z"/><path d="M13.5 6.5l4 4"/></svg>'
ICO_ADM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z"/><path d="M12 8.2l1.2 2.5 2.7.4-2 1.9.5 2.7-2.4-1.3-2.4 1.3.5-2.7-2-1.9 2.7-.4z"/></svg>'

# ---------- HTML ----------
rep('''      <button class="ib" id="membersBtn" title="Membros"></button>
    </div>
''', '''      <button class="ib" id="membersBtn" title="Membros"></button>
    </div>
    <nav id="menuTop" aria-label="Páginas do clã"></nav>
''')
rep('<section id="recView" hidden></section>', '<section id="recView" hidden></section>\n    <section id="jogosView" hidden></section>\n    <section id="visualView" hidden></section>')
rep('<label class="chk"><input type="checkbox" id="cdAnim" checked>', '<label class="chk" hidden><input type="checkbox" id="cdAnim" checked>')
rep('<button class="btn ghost" id="openVisual" type="button">🎨 Aparência</button>', '<button class="btn ghost" id="openVisual" type="button">🎨 Visual do perfil</button>')

# ---------- JS ----------
# Clã na lateral: só o Início
a = s.index('let h = `<div class="cla-mobile">'); b = s.index('</div>`;', a) + len('</div>`;')
s = s[:a] + "let h = `<div class=\"cla-mobile\"><div class=\"cat\">Clã</div><button class=\"ch ${S.view === 'home' ? 'active' : ''}\" data-home>${ICON.home}<span class=\"grow\">Início</span></button></div>`;" + s[b:]

# renderAll: páginas novas + menu de cima
rep("renderTop(); renderTyping(); if (S.view === 'home') renderHome(); }",
    "renderTop(); renderTyping(); if (S.view === 'home') renderHome(); renderMenuTop(); }")
# títulos
rep("  else if (S.view === 'placar') $('#topTitle').innerHTML = `${ICON_PLACAR}<span>Placar PvP do clã</span>`;",
    "  else if (S.view === 'placar') $('#topTitle').innerHTML = `${ICON_PLACAR}<span>Placar PvP do clã</span>`;\n  else if (S.view === 'jogos') $('#topTitle').innerHTML = `" + ICO_CTRL.replace('<svg ', '<svg width="20" height="20" ') + "<span>Jogos</span>`;\n  else if (S.view === 'visual') $('#topTitle').innerHTML = `" + ICO_COR.replace('<svg ', '<svg width="20" height="20" ') + "<span>Visual do perfil</span>`;")
# cliques globais
rep("  if (e.target.closest('[data-rabisco]')) return alternarRabisco();",
    "  if (e.target.closest('[data-rabisco]')) return alternarRabisco();\n  if (e.target.closest('[data-jogos]')) return showJogos();\n  if (e.target.closest('[data-visual]')) return showVisual();\n  if (e.target.closest('#menuTop [data-map]')) return showMap();\n  if (e.target.closest('#menuTop [data-mtadm]')) return $('#admCentralBtn').click();")
# Configurações > Visual abre a página
rep("$('#openVisual').onclick = () => { $('#settings').close(); abrirVisual(); };",
    "$('#openVisual').onclick = () => { $('#settings').close(); showVisual('perfil'); };")
rep("  previaCartao();\n  if (!$('#dlgVisual').open) $('#dlgVisual').showModal();\n}", "  previaCartao();\n}")

# avatar com moldura
rep("""  return `<div class="av ${cls}" ${id ? `data-speak="${esc(id)}"` : ''} style="background:${f ? '#000' : colorFor(name)}">${f ? `<img src="${f}" alt="">` : esc(initials(name))}</div>`; };""",
    """  const mo = moldDe(uid);
  return `<div class="av ${cls}${mo ? ' temmold' : ''}" ${id ? `data-speak="${esc(id)}"` : ''} style="background:${f ? '#000' : colorFor(name)}">${f ? `<img src="${f}" alt="">` : esc(initials(name))}${mo ? `<span class="vmold vm-${mo}" aria-hidden="true"></span>` : ''}</div>`; };""")
# selo junto com o cargo
rep("function tagCargo(uid) { return tagCargoNome(S.cla?.[uid]?.titulo); }",
    "function tagCargo(uid) { return tagCargoNome(S.cla?.[uid]?.titulo) + seloDe(uid); }")
# cor do nick: mensagens, membros, carta
rep('<b class="quem" data-uid="${esc(m.uid || \'\')}"', '<b class="quem${nickCls(m.uid)}" data-uid="${esc(m.uid || \'\')}"')
rep('<div class="who"><b style="${corCargo(p.uid) ? \'color:\' + corCargo(p.uid) : \'\'}">', '<div class="who"><b class="${nickCls(p.uid)}" style="${corCargo(p.uid) ? \'color:\' + corCargo(p.uid) : \'\'}">')
rep('<div class="nm"><b>${esc(o.nome)}</b>', '<div class="nm"><b class="${nickCls(o.uid, o.cd)}">${esc(o.nome)}</b>')
# efeito por cima da carta
rep("    </div>${o.fim || ''}</div>`;\n}", "    </div>${o.cd?.ef ? `<span class=\"vef ve-${o.cd.ef}\" aria-hidden=\"true\"></span>` : ''}${o.fim || ''}</div>`;\n}")

# cartaoValido aceita os enfeites
rep("""  const n = c.n === false ? false : undefined;
  if (e === 'padrao' && !cor && !t && !c.b && n === undefined) return null;
  return { e, c: cor, t, b: !!c.b, ...(n === false ? { n } : {}) };""",
"""  const n = c.n === false ? false : undefined;
  const ex = {}; for (const k of ['mo', 'ef', 'nk', 'se']) if (VIS[k].some(x => x.id === c[k])) ex[k] = c[k];
  if (e === 'padrao' && !cor && !t && !c.b && n === undefined && !Object.keys(ex).length) return null;
  return { e, c: cor, t, b: !!c.b, ...(n === false ? { n } : {}), ...ex };""")

JS_VIS = r'''
// 1.68: enfeites do perfil (grátis, todos veem). Vão no cartão 'cd' da presença: mo moldura, ef efeito, nk cor do nick, se selo.
const VIS = {
  mo: [{ id: 'brasa', nome: 'Brasa', d: 'Anel de fogo girando' }, { id: 'toxico', nome: 'Tóxico', d: 'Faixa de risco verde' }, { id: 'radar', nome: 'Radar', d: 'Varredura de radar' }, { id: 'arame', nome: 'Arame farpado', d: 'Cerca da base' }, { id: 'gelo', nome: 'Gelo', d: 'Brilho frio pulsando' }, { id: 'sangue', nome: 'Sangue', d: 'Anel vermelho' }, { id: 'coroa', nome: 'Coroa', d: 'Só dono e admins', lid: 1 }],
  ef: [{ id: 'neve', nome: 'Neve', d: 'Neve caindo na carta' }, { id: 'brasas', nome: 'Brasas', d: 'Faíscas subindo' }, { id: 'gas', nome: 'Gás tóxico', d: 'Névoa verde' }, { id: 'scan', nome: 'Scanner', d: 'Linha de varredura' }],
  nk: [{ id: 'fogo', nome: 'Fogo', d: 'Nick em degradê de fogo' }, { id: 'gelo', nome: 'Gelo', d: 'Nick azul-gelo' }, { id: 'ouro', nome: 'Ouro', d: 'Nick dourado' }, { id: 'toxico', nome: 'Tóxico', d: 'Nick verde brilhando' }],
  se: [{ id: 'vet', nome: 'Veterano' }, { id: 'sniper', nome: 'Sniper' }, { id: 'medico', nome: 'Médico' }, { id: 'batedor', nome: 'Batedor' }, { id: 'construtor', nome: 'Construtor' }, { id: 'motorista', nome: 'Motorista' }],
  prova: null, aba: 'perfil', cat: 'mo',
};
const ehLid = uid => !!uid && (uid === S.dono || S.cla?.[uid]?.cargo === 'admin');
const CDC = { t: 0, m: new Map() };
function cdDe(uid) {
  if (!uid) return null;
  if (uid === S.uid) return VIS.prova || meuCartao();
  if (Date.now() - CDC.t > 400) { CDC.t = Date.now(); CDC.m = new Map(); try { for (const p of Object.values(S.peers || {})) if (p.uid && p.cd) CDC.m.set(p.uid, p.cd); for (const [u, r] of Object.entries(S.rt || {})) if (r.cd && !CDC.m.has(u)) CDC.m.set(u, r.cd); } catch (e) {} }
  return CDC.m.get(uid) || null;
}
function moldDe(uid) { const mo = cdDe(uid)?.mo; return mo && (mo !== 'coroa' || ehLid(uid)) ? mo : ''; }
function nickCls(uid, cd) { const nk = (cd || cdDe(uid))?.nk; return nk ? ' vn-' + nk : ''; }
function seloDe(uid) { const se = VIS.se.find(x => x.id === cdDe(uid)?.se); return se ? `<span class="vselo vs-${se.id}">${se.nome}</span>` : ''; }
'''
rep("// cartão: vem de cada pessoa pela presença; tudo validado antes de virar estilo\nfunction cartaoValido(c) {",
    JS_VIS + "// cartão: vem de cada pessoa pela presença; tudo validado antes de virar estilo\nfunction cartaoValido(c) {")

JS_PAG = r'''
/* ===================== 1.68: menu de cima, Jogos, Visual do perfil, desempenho ===================== */
const ICO_CTRL = '__CTRL__', ICO_COR = '__COR__', ICO_ADM = '__ADM__';
function renderMenuTop() {
  const nav = $('#menuTop'); if (!nav) return;
  $('#jogosView').hidden = S.view !== 'jogos'; $('#visualView').hidden = S.view !== 'visual';
  const adm = S.eu?.cargo === 'admin', jogando = typeof R !== 'undefined' && everyone().some(p => p.rj);
  const mi = (attr, v, ico, nome, pt = '') => `<button class="mi${S.view === v ? ' on' : ''}" type="button" ${attr}${S.view === v ? ' aria-current="page"' : ''}>${ico}<span>${nome}</span>${pt}</button>`;
  const h = mi('data-map', 'map', ICON.map, 'Mapa') + mi('data-placar', 'placar', ICON_PLACAR, 'Placar PvP')
    + mi('data-vaq', 'vaq', ICON_VAQ, 'Vaquinha', vaqFalta() ? '<i class="pt" aria-label="vaquinha aberta"></i>' : '')
    + mi('data-regras', 'regras', ICON_REGRAS, 'Regras', S.assinou === false ? '<i class="pt red" aria-label="falta assinar"></i>' : '')
    + mi('data-jogos', 'jogos', ICO_CTRL, 'Jogos', jogando ? '<i class="pt" aria-label="tem gente jogando"></i>' : '')
    + '<span class="sep"></span>' + mi('data-visual', 'visual', ICO_COR, 'Visual')
    + (adm ? `<button class="mib${S.view === 'adm' ? ' on' : ''}" type="button" data-mtadm title="Central do Admin" aria-label="Central do Admin">${ICO_ADM}</button>` : '');
  if (nav.innerHTML !== h) nav.innerHTML = h;
  if (S.view === 'jogos') renderJogos();
  const cd = meuCartao(), ch = (cd?.mo || '') + '|' + (cd?.nk || '') + '|' + S.name;
  if (renderMenuTop.eu !== ch && $('#meAv') && typeof selfId !== 'undefined') { renderMenuTop.eu = ch;
    $('#meAv').outerHTML = avatar(S.name, '', selfId, S.uid).replace('class="av ', 'id="meAv" title="Meu perfil" class="av '); $('#meAv').onclick = abrirPerfil;
    $('#meName').className = nickCls(S.uid).trim(); }
}
function mostrarSo(id) { document.querySelectorAll('main > section').forEach(x => x.hidden = x.id !== id); $('#app').classList.remove('menu'); }
function showJogos() { S.view = 'jogos'; mostrarSo('jogosView'); renderAll(); }
function renderJogos() {
  const quem = typeof naSalaR === 'function' ? naSalaR().length : 0, aberto = typeof R !== 'undefined' && R.aberto;
  const h = `<div class="vwrap"><div class="vtit"><span class="vqrot">Jogos do clã</span><h2>Jogos</h2></div>
  <div class="jogos">
    <article class="jogo"><div class="capa" aria-hidden="true"><svg viewBox="0 0 200 100" fill="none" stroke="#1a1410" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M30 75 L60 35 L85 60 L110 25 L140 70 M120 80 Q150 20 175 55 M40 30 q10 -12 22 0"/></svg></div>
      <div class="q"><h3>Rabisco</h3><p>Um desenha, o resto adivinha. Dá para jogar com quem está online, até sem estar na call.</p>
      <div class="rod"><button class="btn acc" type="button" data-rabisco>${aberto ? 'Fechar o Rabisco' : 'Jogar agora'}</button><small>${quem ? quem + (quem === 1 ? ' pessoa' : ' pessoas') + ' no Rabisco' : 'Ninguém jogando agora'}</small></div></div></article>
    <article class="jogo"><div class="capa breve">Em breve</div><div class="q"><h3>Próximo jogo</h3><p>Espaço reservado para o próximo jogo do clã.</p></div></article>
  </div></div>`;
  const box = $('#jogosView'); if (box.dataset.h !== h) { box.dataset.h = h; box.innerHTML = h; }
}

/* ---------- Visual do perfil ---------- */
const VCATS = [{ k: 'mo', nome: 'Molduras' }, { k: 'ef', nome: 'Efeitos' }, { k: 'nk', nome: 'Cor do nick' }, { k: 'se', nome: 'Selos' }, { k: 'e', nome: 'Fundos' }];
function showVisual(aba) { if (typeof aba === 'string') VIS.aba = aba; S.view = 'visual'; mostrarSo('visualView'); renderVisual(); renderAll(); $('#visualView').scrollTop = 0; }
function itensCat(k) { return k === 'e' ? CARTOES.map(x => ({ id: x.id, nome: x.nome, d: 'Fundo do perfil e da carta', f: x.f })) : VIS[k]; }
function visVis(k, it, cd) {
  const nome = S.name || 'Você';
  if (k === 'mo') { VIS.prova = { ...(cd || {}), mo: it.id }; const h = avatar(nome, '', '', S.uid); VIS.prova = null; return it.lid && !ehLid(S.uid) ? h.replace(' temmold', ' temmold').replace('<span class="vmold', '<span class="vmold') : h; }
  if (k === 'ef') return `<div class="vmini"><span class="vef ve-${it.id}"></span>${avatar(nome, '', '', S.uid)}</div>`;
  if (k === 'nk') return `<span class="vnome vn-${it.id}">${esc(nome)}</span>`;
  if (k === 'se') return `<span class="vselo vs-${it.id}" style="font-size:14px;padding:4px 10px">${esc(it.nome)}</span>`;
  return `<span class="vfundo" style="--cf:${it.f}"></span>`;
}
function perfilHtml(cd) {
  const f = CARTOES.find(x => x.id === (cd?.e || 'padrao'))?.f || CARTOES[0].f, nome = S.name || 'Você';
  VIS.prova = cd || {}; const av = avatar(nome, '', '', S.uid); VIS.prova = null;
  const se = VIS.se.find(x => x.id === cd?.se);
  return `<div class="vperfil">${cd?.ef ? `<span class="vef ve-${cd.ef}"></span>` : ''}<div class="vban" style="--cf:${f}"></div><div class="vfoto">${av}</div>
    <div class="vdados"><b class="${(cd?.nk ? 'vn-' + cd.nk : '')}">${esc(nome)}</b><span>${tagCargoNome(S.cla?.[S.uid]?.titulo)}${se ? `<span class="vselo vs-${se.id}" style="margin:0">${se.nome}</span>` : ''}</span><small>${cd?.t ? '“' + esc(cd.t) + '”' : 'Membro do U.C.B.R'}</small></div></div>`;
}
function renderVisual() {
  const box = $('#visualView'); if (!box) return;
  if (!box.dataset.ok) {
    box.dataset.ok = 1;
    box.innerHTML = `<div class="vwrap"><div class="vtit"><span class="vqrot">Tudo de aparência num lugar só</span><h2>Visual do perfil</h2></div>
      <div class="vabas" role="tablist">${[['perfil', 'Perfil'], ['cor', 'Cor do app'], ['carta', 'Carta da sala'], ['desemp', 'Desempenho']].map(([k, n]) => `<button class="vaba" type="button" role="tab" data-vaba="${k}">${n}</button>`).join('')}</div>
      <div id="vPerfil"></div>
      <div id="vCor" class="vsecpg"></div>
      <div id="vCarta" class="vsecpg"></div>
      <div id="vDesemp"></div></div>`;
    const secs = document.querySelectorAll('#dlgVisual .vsec');
    if (secs[0]) { $('#vCor').appendChild(secs[0]); $('#vCor').insertAdjacentHTML('beforeend', '<div class="vopc"><div><b>Voltar ao padrão</b><small>Tira a cor, o fundo, a carta e os enfeites do perfil.</small></div><button class="btn ghost" type="button" data-visreset>Voltar ao padrão</button></div>'); }
    if (secs[1]) $('#vCarta').appendChild(secs[1]);
    box.addEventListener('click', visClique);
    box.addEventListener('pointerover', e => { const it = e.target.closest('[data-vis]'); if (it) provar(it.dataset.vis); });
    box.addEventListener('pointerout', e => { const it = e.target.closest('[data-vis]'); if (it && !it.contains(e.relatedTarget)) provar(''); });
  }
  document.querySelectorAll('#visualView [data-vaba]').forEach(b => { b.classList.toggle('on', b.dataset.vaba === VIS.aba); b.setAttribute('aria-selected', b.dataset.vaba === VIS.aba); });
  $('#vPerfil').hidden = VIS.aba !== 'perfil'; $('#vCor').hidden = VIS.aba !== 'cor'; $('#vCarta').hidden = VIS.aba !== 'carta'; $('#vDesemp').hidden = VIS.aba !== 'desemp';
  if (VIS.aba === 'cor' || VIS.aba === 'carta') abrirVisual();
  if (VIS.aba === 'perfil') renderVisPerfil();
  if (VIS.aba === 'desemp') renderDesemp();
}
function renderVisPerfil() {
  const cd = meuCartao() || {}, k = VIS.cat;
  const itens = itensCat(k);
  const nenhum = k === 'e' ? '' : `<button class="vitem${!cd[k] ? ' usando' : ''}" type="button" data-vis="${k}|"><div class="vvis"><span class="vnome" style="color:var(--txt3)">—</span></div><div class="vinfo"><b>Nenhum</b><small>Sem ${VCATS.find(x => x.k === k).nome.toLowerCase()}</small><span class="vest${!cd[k] ? ' on' : ''}">${!cd[k] ? 'Usando' : 'Tirar'}</span></div></button>`;
  const grade = nenhum + itens.map(it => { const on = (cd[k] || (k === 'e' ? 'padrao' : '')) === it.id, bloq = it.lid && !ehLid(S.uid);
    return `<button class="vitem${on ? ' usando' : ''}" type="button" data-vis="${k}|${it.id}"${bloq ? ' aria-disabled="true"' : ''}><div class="vvis">${visVis(k, it, cd)}</div>${it.lid ? '<span class="vtag lid">Liderança</span>' : ''}<div class="vinfo"><b>${esc(it.nome)}</b><small>${esc(it.d || 'Selo ao lado do nick')}</small><span class="vest${on ? ' on' : ''}">${on ? 'Usando' : bloq ? 'Só dono e admins' : 'Grátis'}</span></div></button>`; }).join('');
  $('#vPerfil').innerHTML = `<div class="vcorpo"><div class="vlista"><div class="vfiltro" role="tablist">${VCATS.map(c => `<button type="button" data-vcat="${c.k}" class="${c.k === k ? 'on' : ''}">${c.nome}</button>`).join('')}</div>
    <div class="vgrade">${grade}</div></div>
    <aside class="vlado" id="vLado"><span class="vqrot">Seu perfil</span>${perfilHtml(cd)}<p class="vdica">Todos do clã veem estes enfeites no seu nick, na sua foto e na sua carta da sala. Passe o mouse num item para provar. É tudo grátis.</p></aside></div>`;
}
function provar(v) {
  const lado = $('#vLado'); if (!lado) return;
  const cd = meuCartao() || {};
  if (!v) { lado.classList.remove('provando'); lado.innerHTML = `<span class="vqrot">Seu perfil</span>${perfilHtml(cd)}<p class="vdica">Todos do clã veem estes enfeites no seu nick, na sua foto e na sua carta da sala. Passe o mouse num item para provar. É tudo grátis.</p>`; return; }
  const [k, id] = v.split('|'), it = itensCat(k).find(x => x.id === id);
  lado.classList.add('provando');
  lado.innerHTML = `<span class="vqrot">Provando: <em>${esc(it?.nome || 'Nenhum')}</em></span>${perfilHtml({ ...cd, [k]: id || undefined })}<p class="vdica">Clique para usar. Clique de novo para tirar.</p>`;
}
function visClique(e) {
  const ab = e.target.closest('[data-vaba]'); if (ab) { VIS.aba = ab.dataset.vaba; return renderVisual(); }
  const c = e.target.closest('[data-vcat]'); if (c) { VIS.cat = c.dataset.vcat; return renderVisPerfil(); }
  if (e.target.closest('[data-visreset]')) { $('#visReset').click(); return; }
  const n = e.target.closest('[data-nivel]'); if (n) { LS.set('nivelAnim', n.dataset.nivel); aplicarNivel(); return renderDesemp(); }
  const op = e.target.closest('[data-opc]'); if (op) { LS.set(op.dataset.opc, !LS.get(op.dataset.opc, true)); if (!LS.get('pausarFundo', true)) document.body.classList.remove('parado'); return renderDesemp(); }
  const it = e.target.closest('[data-vis]'); if (!it) return;
  const [k, id] = it.dataset.vis.split('|'), item = itensCat(k).find(x => x.id === id);
  if (item?.lid && !ehLid(S.uid)) return toast('A coroa é só para o dono e os admins.');
  const cd = { ...(LS.get('cartao', {}) || {}) }, atual = cd[k] || (k === 'e' ? 'padrao' : '');
  if (!id || atual === id) { if (k === 'e') cd.e = 'padrao'; else delete cd[k]; } else cd[k] = id;
  LS.set('cartao', cd); CDC.t = 0; salvarCartao({}); renderVisPerfil(); renderAll(); if (S.view === 'text') renderMessages();
}
/* ---------- desempenho ---------- */
const nivelPadrao = () => ((navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4) ? 'leve' : 'completo';
const nivelAnim = () => { const n = LS.get('nivelAnim', ''); return ['completo', 'equilibrado', 'leve'].includes(n) ? n : nivelPadrao(); };
function aplicarNivel() {
  const n = nivelAnim();
  document.body.classList.toggle('anim-equi', n === 'equilibrado'); document.body.classList.toggle('anim-leve', n === 'leve');
  LS.set('semAnim', n === 'leve'); semAnim();
  if (typeof renderStage === 'function' && S.main) renderStage();
}
function renderDesemp() {
  const n = nivelAnim(), pf = LS.get('pausarFundo', true);
  const NV = [['completo', 'Completo', 'Tudo animado: cartas, molduras, efeitos e nicks.'], ['equilibrado', 'Equilibrado', 'Enfeites só se mexem com o mouse em cima. Sem desfoque.'], ['leve', 'Leve', 'Nada se mexe. O melhor para PC fraco e para o FPS do jogo.']];
  $('#vDesemp').innerHTML = `<div class="vsecpg"><b>Animações</b><p class="vdica">Vale só para este PC. Os outros continuam vendo os seus enfeites.</p>
    <div class="niveis" role="radiogroup" aria-label="Animações">${NV.map(([k, t, d]) => `<button type="button" class="nivel${n === k ? ' on' : ''}" role="radio" aria-checked="${n === k}" data-nivel="${k}"><b>${t}</b><small>${d}</small></button>`).join('')}</div>
    <div class="vopc"><div><b>Pausar quando o app não está na frente</b><small>Com o DayZ aberto ou o app minimizado, nada se mexe. A voz continua normal.</small></div><button type="button" class="chave" role="switch" aria-checked="${!!pf}" aria-label="Pausar quando o app não está na frente" data-opc="pausarFundo"></button></div>
    <p class="vdica">Este PC: ${navigator.hardwareConcurrency || '?'} núcleos${navigator.deviceMemory ? ', ' + navigator.deviceMemory + ' GB de memória (aprox.)' : ''}. ${LS.get('nivelAnim', '') ? '' : 'Escolhemos "' + NV.find(x => x[0] === n)[1] + '" sozinhos para este PC.'}</p></div>`;
}
aplicarNivel();
// app sem foco ou minimizado: para as animações (clicar no mapa ou no vídeo, que são do próprio app, não conta)
(() => {
  const liga = v => document.body.classList.toggle('parado', v && LS.get('pausarFundo', true));
  window.addEventListener('blur', () => setTimeout(() => { if (document.activeElement?.tagName !== 'IFRAME') liga(true); }, 0));
  window.addEventListener('focus', () => liga(false));
  document.addEventListener('visibilitychange', () => liga(document.hidden));
})();
'''
JS_PAG = JS_PAG.replace('__CTRL__', ICO_CTRL).replace('__COR__', ICO_COR).replace('__ADM__', ICO_ADM)
# entra no fim do script principal
k = s.rindex('\nboot();')
s = s[:k] + JS_PAG + s[k:]

# versão
n = len(re.findall(r"versao: '1\.67'", s))
s = re.sub(r"versao: '1\.67'", "versao: '1.68'", s)
s = re.sub(r"dataVersao: '[^']*'", "dataVersao: '23/11/2026'", s)
print('versao trocada', n)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
