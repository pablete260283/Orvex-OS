"""Build the standalone preview with embedded source data, brand assets, JS and CSS."""
from pathlib import Path
import base64,json
ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'src/orvex/ui/assets'
def uri(path,mime):return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
logo=uri(assets/'brand/svg/orvex-horizontal-dark.svg','image/svg+xml')
fallback=uri(assets/'brand/png/orvex-horizontal-dark-4x.png','image/png')
icon=uri(assets/'brand/svg/orvex-app-icon-dark.svg','image/svg+xml')
art={p.stem:uri(p,'image/svg+xml') for p in sorted(assets.glob('*.svg'))}
catalog=json.loads((ROOT/'src/orvex/core/demo.json').read_text())
serial=lambda data:json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
html='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ORVEX OS 0.2 · Visual Preview</title>'''
html+=f'<link rel="icon" href="{icon}"><style>'+(ROOT/'web/style.css').read_text()+'</style>'
html+=f'''<div id="stage"><div id="backdrop" aria-hidden="true"><div class="bg-base"></div><div class="bg-next"></div></div><header><img class="logo" width="610" height="165" src="{logo}" alt="ORVEX OS" onerror="this.onerror=null;this.src='{fallback}'"><nav aria-label="Principal"></nav><button id="profile" data-action="profile" data-focus="profile"></button><span id="storage" role="status"></span></header><main></main><footer>Flechas / Tab Navegar　 Enter Elegir　 Esc Volver　 F11 Pantalla completa<span>0.2 DEMO · Perfiles sin PIN ni protección real</span></footer></div>'''
html+='<script>const ORVEX_PROGRESS='+serial(json.loads((ROOT/'src/orvex/core/demo_progress.json').read_text()))+';const ORVEX_DEMO='+serial(catalog)+';const ORVEX_ART='+serial(art)+';</script>'
for name in ['library.js','app.js']:html+='<script>'+(ROOT/'web'/name).read_text()+'</script>'
html+='</html>'
(ROOT/'preview/ORVEX-0.2.html').write_text(html,encoding='utf-8')
print('Built preview/ORVEX-0.2.html')
