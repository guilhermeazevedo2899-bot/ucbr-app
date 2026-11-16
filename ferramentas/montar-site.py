#!/usr/bin/env python3
"""Copia a plataforma (pasta do zip) para desk/site e troca tudo que vinha da internet por cópias locais.
Uso: python3 ferramentas/montar-site.py <pasta-da-plataforma> <pasta-libs-extraidas>"""
import sys, shutil, pathlib, re
src, libs = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst = pathlib.Path(__file__).resolve().parent.parent / 'site'
if dst.exists(): shutil.rmtree(dst)
dst.mkdir()
for n in ['index.html', 'versao.json', 'manifest.webmanifest', 'mapa-chernarus.jpg', 'regras-ucbr.pdf', 'whatsapp-qr.png']:
    shutil.copy2(src / n, dst / n)
for d in ['icones', 'mapa3d', 'ruido']:
    shutil.copytree(src / d, dst / d)
lib = dst / 'lib'; (lib / 'fontes').mkdir(parents=True)
sb = libs / 'supabase-supabase-js-2.45.4/package/dist/umd'
for f in sb.glob('*.js'): shutil.copy2(f, lib / f.name)
shutil.copy2(libs / 'three-0.128.0/package/build/three.min.js', lib / 'three.min.js')
shutil.copy2(libs / 'three-0.128.0/package/examples/js/controls/OrbitControls.js', lib / 'OrbitControls.js')
fontes = [('Permanent Marker', 400, 'fontsource-permanent-marker-5.3.0/package/files/permanent-marker-latin-400-normal.woff2'),
          ('Barlow Condensed', 600, 'fontsource-barlow-condensed-5.3.0/package/files/barlow-condensed-latin-600-normal.woff2'),
          ('Barlow Condensed', 700, 'fontsource-barlow-condensed-5.3.0/package/files/barlow-condensed-latin-700-normal.woff2'),
          ('Barlow Condensed', 400, 'fontsource-barlow-condensed-5.3.0/package/files/barlow-condensed-latin-400-normal.woff2'),
          ('Barlow Condensed', 500, 'fontsource-barlow-condensed-5.3.0/package/files/barlow-condensed-latin-500-normal.woff2'),
          ('Barlow', 400, 'fontsource-barlow-5/package/files/barlow-latin-400-normal.woff2'),
          ('Barlow', 500, 'fontsource-barlow-5/package/files/barlow-latin-500-normal.woff2'),
          ('Barlow', 600, 'fontsource-barlow-5/package/files/barlow-latin-600-normal.woff2')]
css = ''
for fam, w, p in fontes:
    nome = pathlib.Path(p).name; shutil.copy2(libs / p, lib / 'fontes' / nome)
    css += f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(fontes/{nome}) format('woff2')}}\n"
(lib / 'fontes.css').write_text(css)

def troca(arq, pares):
    s = arq.read_text(encoding='utf-8')
    for a, b in pares:
        if a not in s: sys.exit(f'não achei em {arq.name}: {a[:80]}')
        s = s.replace(a, b)
    arq.write_text(s, encoding='utf-8')

troca(dst / 'index.html', [
    ('<link rel="preconnect" href="https://fonts.googleapis.com">\n', ''),
    ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', ''),
    ('<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Permanent+Marker&display=swap" rel="stylesheet">', '<link href="lib/fontes.css" rel="stylesheet">'),
    ('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.45.4/dist/umd/supabase.js', 'lib/supabase.js'),
])
troca(dst / 'mapa3d/index.html', [
    ('<link rel="preconnect" href="https://fonts.googleapis.com">\n', ''),
    ('<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">', '<link href="../lib/fontes.css" rel="stylesheet">'),
    ('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js', '../lib/OrbitControls.js'),('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js', '../lib/three.min.js')])
left = re.findall(r'https://(?:fonts\.googleapis|cdn\.jsdelivr|cdnjs|unpkg)[^\s"\')]*', (dst / 'index.html').read_text() + (dst / 'mapa3d/index.html').read_text())
print('site montado em', dst, '| externos restantes:', left or 'nenhum')
