/* Pure demo-library/session model, used by the offline preview and Node tests. */
(function(root){
'use strict';
const normalize=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
const allowed=(e,p)=>p==='adult'||p==='child'&&Number.isInteger(e.age)&&e.age>=0&&e.age<=7;
function createSession(catalog,storage,progress={}){
 let available=true,cache={};
 const get=(k,d)=>{try{const v=storage.getItem(k);return v===null?d:JSON.parse(v)}catch{return d}};
 const put=(k,v)=>{cache[k]=v;try{storage.setItem(k,JSON.stringify(v))}catch{available=false}};
 let profile=get('orvex-v2-profile','adult');if(!['adult','child'].includes(profile))profile='adult';
 let favorites=get('orvex-v2-favorites',{adult:[],child:[]});if(!favorites||typeof favorites!=='object')favorites={};
 for(const p of ['adult','child'])if(!Array.isArray(favorites[p]))favorites[p]=[];
 let focused='',backgroundMode=get('orvex-v2-background-mode','dynamic'),fixedBackground=get('orvex-v2-background-fixed','aurora');
 if(!['dynamic','fixed','default'].includes(backgroundMode))backgroundMode='dynamic';
 const states={};let page=0,detailId='',motion=get('orvex-preview-motion',false)===true;
 const state=()=>states[profile+page]||(states[profile+page]={query:'',category:'Todas',favorites:false,index:0});
 const visible=(kind=null)=>catalog.filter(e=>allowed(e,profile)&&(!kind||e.kind===kind));
 const annotate=e=>({...e,favorite:favorites[profile].includes(e.id),...(e.kind==='game'?{progress:present(progress[e.id])}:{})});
 function present(record){if(!record)return {};return {...record,source:'demo',percentLabel:record.percent===null?'Sin porcentaje disponible':record.percent+'%',timeLabel:record.minutes===null?'Tiempo no disponible':Math.floor(record.minutes/60)+' h '+record.minutes%60+' min',lastLabel:record.last_session||'Sin sesiones',statusLabel:({not_started:'No iniciado',in_progress:'En progreso',completed:'Completado'})[record.status]||'Sin información'}}
 const api={
 get profile(){return profile},get page(){return page},get motion(){return motion},get persistent(){return available},state,
 options(){let field=page===2?'media_type':'platform';return ['Todas',...new Set(visible(page===2?'media':'game').map(e=>e[field]))].sort((a,b)=>a==='Todas'?-1:b==='Todas'?1:a.localeCompare(b))},
 entries(){if(page===0)return visible('game').filter(e=>progress[e.id]?.last_session).sort((a,b)=>progress[b.id].last_session.localeCompare(progress[a.id].last_session)).slice(0,4).map(annotate);if(page===3)return [];const s=state(),field=page===2?'media_type':'platform';return visible(page===2?'media':'game').filter(e=>normalize(e.title).includes(normalize(s.query.trim()))&&(s.category==='Todas'||e[field]===s.category)&&(!s.favorites||favorites[profile].includes(e.id))).map(annotate)},
 detail(){const e=visible().find(e=>e.id===detailId);return e?annotate(e):null},
 navigate(p){if(![0,1,2,3].includes(p))return;page=p;detailId=''},
 setProfile(p){if(!['adult','child'].includes(p)||p===profile)return;profile=p;detailId='';focused='';put('orvex-v2-profile',p)},
 setQuery(q){state().query=q;state().index=0},
 setCategory(c){if(api.options().includes(c)){state().category=c;state().index=0}},
 toggleFavorites(){state().favorites=!state().favorites;state().index=0},
 clearFilters(){Object.values(states).forEach(s=>Object.assign(s,{query:'',category:'Todas',favorites:false,index:0}))},
 select(i){if(i>=0&&i<api.entries().length)state().index=i},
 open(i){const e=api.entries()[i];if(e){state().index=i;detailId=e.id}},
 close(){detailId=''},
 toggleFavorite(id){if(!visible().some(e=>e.id===id))return false;const list=favorites[profile];favorites[profile]=list.includes(id)?list.filter(x=>x!==id):[...list,id];put('orvex-v2-favorites',favorites);state().index=Math.min(state().index,Math.max(0,api.entries().length-1));return true},
 get backgroundMode(){return backgroundMode},get fixedBackground(){return fixedBackground},
 backgroundOptions(){return visible().map(e=>({id:e.id,title:e.title}))},
 featured(){return api.entries().find(e=>e.id===focused)||api.entries()[0]||null},
 focus(id){if(api.entries().some(e=>e.id===id)){focused=id;api.select(api.entries().findIndex(e=>e.id===id))}},
 backgroundArt(){if(backgroundMode==='default')return '';if(backgroundMode==='fixed')return visible().find(e=>e.id===fixedBackground)?.art||'';return (api.detail()||api.featured())?.art||''},
 setBackgroundMode(mode){if(['dynamic','fixed','default'].includes(mode)){backgroundMode=mode;put('orvex-v2-background-mode',mode)}},
 setFixedBackground(id){if(visible().some(e=>e.id===id)){fixedBackground=id;put('orvex-v2-background-fixed',id)}},
 toggleMotion(){motion=!motion;put('orvex-preview-motion',motion)}
 };return api;
}
const exports={normalize,allowed,createSession};if(typeof module!=='undefined'&&module.exports)module.exports=exports;else root.ORVEX=exports;
})(typeof globalThis!=='undefined'?globalThis:this);
