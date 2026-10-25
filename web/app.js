'use strict';
const store={getItem:k=>localStorage.getItem(k),setItem:(k,v)=>localStorage.setItem(k,v)};
const session=ORVEX.createSession(ORVEX_DEMO,store);
const names=['Inicio','Videojuegos','Multimedia','Configuración'],categories=['Interfaz','Controles','Audio','Biblioteca','Perfiles','Sistema'];
let settingsCategory=0,message='';
const stage=document.querySelector('#stage'),main=document.querySelector('main'),nav=document.querySelector('nav');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const age=e=>e.age===0?'General':e.age+'+';
const profileLabel=()=>session.profile==='child'?'Infantil':'Adulto';
const art=e=>ORVEX_ART[e.art];
const card=(e,i)=>`<button class="card" data-action="open" data-index="${i}" data-focus="card${i}"><img alt="" src="${art(e)}"><span class="badge">DEMO</span><strong>${e.favorite?'♥ ':''}${esc(e.title)}</strong><small>${esc(e.platform)} · ${age(e)}</small><small class="open">Abrir ficha →</small></button>`;
function resize(){stage.style.transform=`translate(-50%,-50%) scale(${Math.min(innerWidth/1920,innerHeight/1080)})`}addEventListener('resize',resize);resize();
function focus(key){document.querySelector(`[data-focus="${key}"]`)?.focus()}
function go(p){session.navigate(p);message='';render();focus('nav'+p)}
function detailPage(e){return `<section class="details"><div class="detail-footer">ORVEX OS 0.2 · ${profileLabel()} · Perfiles demostrativos sin PIN</div><button class="back" data-action="back" data-focus="back">← Volver</button><span class="eyebrow">FICHA / CONTENIDO DE DEMOSTRACIÓN</span><img class="cover" src="${art(e)}" alt="Portada de ${esc(e.title)}"><div class="info"><h1>${esc(e.title)}</h1><div class="meta">${esc(e.platform)} · ${age(e)}</div><p class="description">${esc(e.description)}</p><p class="availability">${esc(e.availability)}</p><div class="row"><button class="accent" data-action="play" data-focus="play">${e.kind==='game'?'Jugar':'Ver'} · DEMO</button><button data-action="favorite" data-focus="favorite">${e.favorite?'♥ Quitar de favoritos':'♡ Agregar a favoritos'}</button></div><p role="status" class="message">${esc(message)}</p></div></section>`}
function settingsPage(){let c=settingsCategory;let description=c===0?'FUNCIONAL · Preferencias guardadas en este navegador':c===3?'FUNCIONAL · Filtros y favoritos por perfil':c===4?'DEMO · Filtro infantil hasta 7+. Sin autenticación ni PIN.\nEl cambio de perfil es libre: no es un control parental seguro.':c===5?'FUNCIONAL · ORVEX OS 0.2 Visual Preview\nVista HTML autónoma. La aplicación Qt utiliza SQLite.\nTodo el catálogo es ficticio. Sin conexiones a servicios externos.':'FUTURO · Esta categoría no controla dispositivos.\nLa integración se desarrollará en una próxima fase.';
return `<h1>Configuración</h1><div class="settings"><div class="categories">${categories.map((n,i)=>`<button class="${c===i?'selected':''}" data-action="settings" data-index="${i}" data-focus="setting${i}">${n}</button>`).join('')}</div><section class="panel"><h2>${categories[c]}</h2><p class="${c===1||c===2?'future':''}">${description}</p>${c===0?`<button class="wide" data-action="motion" data-focus="motion">Reducir movimiento: ${session.motion?'Sí':'No'}</button>`:c===3?'<button class="wide" data-action="clear" data-focus="clear">Limpiar filtros de las bibliotecas</button>':c===4?`<div class="row"><button class="${session.profile==='adult'?'selected':''}" data-action="adult" data-focus="adult">Adulto · demo</button><button class="${session.profile==='child'?'selected':''}" data-action="child" data-focus="child">Infantil · demo</button></div>`:''}<p role="status" class="message">${esc(message)}</p></section></div>`}
function render(focusKey=null,caret=null){
 const oldFocus=focusKey||document.activeElement?.dataset.focus;
 document.body.classList.toggle('reduced',session.motion);
 nav.innerHTML=names.map((n,i)=>`<button class="${session.page===i?'selected':''}" ${session.page===i?'aria-current="page"':''} data-action="nav" data-index="${i}" data-focus="nav${i}">${n}</button>`).join('');
 document.querySelector('#profile').textContent=profileLabel()+' · demo ⇄';
 document.querySelector('#storage').textContent=session.persistent?'':'Guardado no disponible: preferencias de esta sesión';
 const e=session.detail(),entries=session.entries();main.className=e?'detail':session.page===0?'home':'';document.querySelector('header').inert=!!e;document.querySelector('footer').hidden=!!e;
 if(e)main.innerHTML=detailPage(e);
 else if(session.page===3)main.innerHTML=settingsPage();
 else if(session.page===0)main.innerHTML=`<section class="hero" style="background-image:url('${ORVEX_ART.aurora}')"><div class="eyebrow">TU ESPACIO. TU MOMENTO.</div><h1>Todo listo para<br>tu próxima aventura.</h1><p>Videojuegos y multimedia, en un solo lugar.</p><button class="accent" data-action="explore" data-focus="explore">Explorar biblioteca →</button></section><h2>${session.profile==='child'?'Para descubrir en familia · General y 7+':'Descubre tu próximo favorito'}</h2><section class="cards">${entries.map(card).join('')}</section>`;
 else{main.innerHTML=`<h1>${session.page===2?'Tu colección multimedia':'Todos tus videojuegos'}</h1><p class="subtitle">Catálogo ficticio · Explora, guarda y descubre</p><div class="toolbar"><input type="search" aria-label="Buscar por nombre" placeholder="Buscar por nombre…" data-focus="search"><select aria-label="${session.page===2?'Tipo':'Plataforma'}" data-focus="filter">${session.options().map(o=>`<option>${esc(o)}</option>`).join('')}</select><button data-action="favorites" data-focus="favorites" class="${session.state().favorites?'selected':''}">${session.state().favorites?'♥ Solo favoritos':'♡ Todos los títulos'}</button><button data-action="clear" data-focus="clear">Limpiar filtros</button></div><p class="count" aria-live="polite">${entries.length} títulos · ${profileLabel()} (demo)</p><section class="cards" aria-label="Títulos de demostración">${entries.length?entries.map(card).join(''):'<div class="empty">No hay títulos con estos filtros.<br>Prueba otra búsqueda o limpia los filtros.</div>'}</section>`;const input=main.querySelector('input');input.value=session.state().query;main.querySelector('select').value=session.state().category;
 input.addEventListener('input',event=>{const pos=event.target.selectionStart;session.setQuery(event.target.value);render('search',pos)});
 input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();focus('card'+session.state().index)}});
 main.querySelector('select').addEventListener('change',event=>{session.setCategory(event.target.value);render('filter')});}
 if(oldFocus)focus(oldFocus);if(caret!==null){const input=main.querySelector('input');if(input){try{input.setSelectionRange(caret,caret)}catch{}}}
}
document.addEventListener('click',event=>{const b=event.target.closest('[data-action]');if(!b)return;const a=b.dataset.action,i=Number(b.dataset.index);message='';
 if(a==='nav'){go(i);return}if(a==='open'){session.open(i);render('back');return}if(a==='back'){session.close();render('card'+session.state().index);return}
 if(a==='profile'){session.setProfile(session.profile==='adult'?'child':'adult')}else if(a==='adult'||a==='child'){session.setProfile(a)}else if(a==='favorite'){session.toggleFavorite(session.detail().id)}else if(a==='favorites'){session.toggleFavorites()}else if(a==='clear'){session.clearFilters();if(session.page===3)message='Filtros restablecidos. Tus favoritos se conservan.'}else if(a==='motion'){session.toggleMotion()}else if(a==='play'){message='Demostración: no hay un lanzador ni un reproductor conectado.'}else if(a==='settings'){settingsCategory=i}else if(a==='explore'){session.navigate(1);render('search');return}render(b.dataset.focus);
});
addEventListener('keydown',event=>{const target=event.target;
 if(event.key==='Escape'){event.preventDefault();if(message){message='';render()}else if(session.detail()){session.close();render('card'+session.state().index)}else go(0);return}
 if(!event.key.startsWith('Arrow'))return;
 if(target.matches('input,select')){if(target.matches('input')&&event.key==='ArrowDown'){event.preventDefault();focus('card'+session.state().index)}return}
 if(target.dataset.action==='nav'&&['ArrowLeft','ArrowRight'].includes(event.key)){event.preventDefault();go((Number(target.dataset.index)+(event.key==='ArrowRight'?1:3))%4);return}
 if(target.dataset.action==='nav'&&event.key==='ArrowDown'){event.preventDefault();focus(session.page===0?'explore':session.page===3?'setting'+settingsCategory:'search');return}
 if(target.classList.contains('card')){event.preventDefault();const i=Number(target.dataset.index);if(event.key==='ArrowUp'&&i<4){focus('search');return}const d={ArrowRight:1,ArrowLeft:-1,ArrowDown:4,ArrowUp:-4}[event.key];const next=Math.max(0,Math.min(session.entries().length-1,i+d));session.select(next);focus('card'+next);return}
 const buttons=[...document.querySelectorAll('button,input,select')].filter(x=>!x.disabled&&!x.closest('[inert]')&&x.getClientRects().length),i=buttons.indexOf(target);if(i>=0){event.preventDefault();buttons[(i+(event.key==='ArrowRight'||event.key==='ArrowDown'?1:buttons.length-1))%buttons.length].focus()}
});
render();focus('nav0');
