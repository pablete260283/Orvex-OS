from PySide6.QtCore import QObject, Property, Signal, Slot
from .progress import DemoProgressProvider, presentation
from .library import LibraryService, PROFILES, normalized
from .installed import InstalledLibrary
from .launcher import GameLauncher
from .local_artwork import LocalArtwork
from pathlib import Path
import tempfile,weakref,sqlite3

class Bridge(QObject):
    operationChanged = Signal()
    changed = Signal()
    visualChanged = Signal()
    libraryChanged = Signal()
    pageChanged = Signal()
    detailChanged = Signal()
    indexChanged = Signal()
    def __init__(self, store, progress_provider=None):
        super().__init__()
        self.store=store
        self.service=LibraryService(store)
        self.progress_provider=progress_provider or DemoProgressProvider()
        self._focused_id=""
        self._page=1
        self._profile=store.get("profile","adult")
        if self._profile not in PROFILES:self._profile="adult"
        self._states={}
        self._detail_id=""
        from ..adapters.dolphin import DolphinAdapter
        self.dolphin=DolphinAdapter(store)
        from ..adapters.pcsx2 import PCSX2Adapter
        self.pcsx2=PCSX2Adapter(store)
        self.installed=InstalledLibrary(store)
        self.launcher=GameLauncher(self.installed,self)
        from ..runtime.quick_menu import QuickMenu
        self.quick_menu=QuickMenu(self.launcher,store,parent=self)
        self.shortcut_capture=False
        self.shortcut_message="Mantén el atajo durante un segundo. F10 abre el menú desde ORVEX."
        self._temp_assets=tempfile.TemporaryDirectory(prefix="orvex-assets-") if store.path is None else None
        if self._temp_assets:weakref.finalize(self,self._temp_assets.cleanup)
        root=Path(self._temp_assets.name) if self._temp_assets else store.path.parent/"artwork"
        self.artwork=LocalArtwork(self.installed,root)
        from ..controls.discovery import SDLInventory
        from ..controls.manager import ControllerManager
        self.controller_inventory=SDLInventory(store.get('dolphin_executable',''))
        self.controllers=ControllerManager(store,self.installed,(root/'controller-profiles' if store.path is None else store.path.parent/'controller-profiles'),self.controller_inventory)
        self.controller_devices=[]
        self.controller_input_error=""
        self.launcher.controller_manager=self.controllers
        from .metadata_local import LocalMetadata
        self.metadata=LocalMetadata(self.installed)
        self._message=self.controllers.recovery if store.get("controller_restore_journal",{}) else ""
        self.launcher.changed.connect(self._launch_updated)
        from PySide6.QtCore import QTimer
        self.romTimer=QTimer(self);self.romTimer.setInterval(10000)
        self.romTimer.timeout.connect(self._poll_roms);self.romTimer.start()
    def _poll_roms(self):
        if getattr(self.store,"closed",False):self.romTimer.stop();return
        if self.store.get("rom_root","") and self._profile=="adult" and not self.launchBusy:self.scanDolphin()
    def _launch_updated(self):
        self._message=self.launcher.message;self.operationChanged.emit();self.refresh();self.detailChanged.emit()
    @Slot(str,result="QVariantMap")
    def browseDirectory(self,value):
        if self._profile!="adult":return dict(directory="",parent="",items=[],error="Disponible en el perfil Adulto.")
        from .installed import local_path
        import os
        try:
            if value=="computer":
                roots=[str(Path(chr(c)+":/")) for c in range(65,91) if Path(chr(c)+":/").is_dir()] if os.name=="nt" else ["/"]
                return dict(directory="computer",parent="computer",items=[dict(name=p,path=p,directory=True) for p in roots],error="")
            folder=local_path(value) if value else Path.home()
            folder=folder.expanduser().resolve(strict=True)
            if not folder.is_dir():raise ValueError("Selecciona una carpeta existente.")
            entries=[]
            for child in sorted(folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())):
                if child.name.startswith("."):continue
                entries.append(dict(name=child.name,path=str(child),directory=child.is_dir()))
                if len(entries)>=1000:break
            return dict(directory=str(folder),parent=str(folder.parent) if folder.parent!=folder else "computer",items=entries,error="Se muestran hasta 1000 elementos; usa Ruta para ir directamente." if len(entries)==1000 else "")
        except (OSError,ValueError) as e:return dict(directory=value,parent="computer",items=[],error="No se pudo abrir la carpeta: "+str(e))
    @Property(QObject,constant=True)
    def inGameMenu(self):return self.quick_menu
    @Property(str,notify=operationChanged)
    def quickMenuShortcutLabel(self):return " + ".join(self.store.get("quick_menu_buttons",["view","menu"]))
    @Property(str,notify=operationChanged)
    def quickMenuCaptureMessage(self):return self.shortcut_message
    @Slot()
    def beginShortcutCapture(self):
        self.shortcut_capture=True
        self.shortcut_message="Suelta todos los botones y mantén la combinación deseada. Volver cancela."
        self.operationChanged.emit()
    def save_quick_shortcut(self,buttons):
        self.store.set("quick_menu_buttons",sorted(buttons));self.shortcut_capture=False
        self.shortcut_message="Atajo guardado: "+self.quickMenuShortcutLabel;self.operationChanged.emit()
    @Slot(str,str,result=bool)
    def approvePauseConfig(self,engine,path):
        if self._profile!="adult" or self.launchBusy or engine not in ("dolphin","pcsx2"):return False
        from .installed import local_path
        from ..runtime.quick_menu import FocusPausePolicy
        try:
            value=str(local_path(path).resolve(strict=True))
            previous=self.store.get("quick_pause_config_"+engine,"")
            self.store.set("quick_pause_config_"+engine,value)
            if not FocusPausePolicy.configured(self.store,engine):
                self.store.set("quick_pause_config_"+engine,previous)
                raise ValueError("Activa pausa al perder foco en el emulador y selecciona su INI activo. ORVEX no lo modifica.")
            self._message="Referencia aprobada; ORVEX solo lee la configuración. Pausa física pendiente de validación."
            self.operationChanged.emit();return True
        except (OSError,ValueError) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot(str)
    def reportControllerInputError(self,message):
        self.controller_input_error=message
        if message:self._message="No se pudo leer el mando. Reconéctalo; puedes usar otro control. Detalle: "+message
        self.operationChanged.emit()
    @Property("QVariantList",notify=operationChanged)
    def controllerDevices(self):return self.controller_devices if self._profile=="adult" else []
    @Property("QVariantList",notify=operationChanged)
    def controllerProfiles(self):return [dict(id=p['id'],name=p['name'],engine=p['engine'],family=p['family'],volatile=p['volatile']) for p in self.controllers.profiles()] if self._profile=="adult" else []
    @Property(str,notify=operationChanged)
    def controllerNotice(self):return self.controllers.notice if self._profile=="adult" else ""
    @Property(bool,notify=operationChanged)
    def controllerAutoApply(self):return self.store.get('controller_apply_enabled',False)
    def _refresh_controllers(self,force):
        if self._profile!="adult":return
        devices=self.controller_inventory.devices()
        for d in devices:d['display']=d['name']+(' · identificado' if d['stable'] else ' · identidad no verificable')+' · sensores: '+d.get('sensors','no verificado')
        if devices==self.controller_devices and not force:return
        self.controller_devices=devices
        self._message=self.controller_inventory.error or ('Mandos detectados: '+str(len(devices)))
        if any(d.get('warning') for d in devices):self._message+=' XInput y SDL/Steam Input podrían duplicar un mando; comprueba antes de asignar.'
        self.operationChanged.emit()
    @Slot()
    def refreshControllers(self):self._refresh_controllers(True)
    @Slot()
    def pollControllers(self):self._refresh_controllers(False)
    @Slot(str,str,str,result=bool)
    def captureControllerProfile(self,url,engine,family):
        if self._profile!="adult" or self.launchBusy:return False
        try:
            from .installed import local_path
            path=local_path(url)
            profile=self.controllers.capture(str(path),path.stem,engine,family)
            self._message='Copia aprobada guardada: '+profile['name']+('. Índice SDL variable: aplicación automática bloqueada.' if profile['volatile'] else '')
            self.operationChanged.emit();return True
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot(str,str,str,str,str,int,result=bool)
    def bindControllerProfile(self,profile_id,game_id,scope,device_id,family,player):
        if self._profile!="adult" or self.launchBusy:return False
        try:
            present=[d for d in self.controller_inventory.devices() if d['device_id']==device_id and d['family']==family and d['stable']]
            if len(present)!=1:raise ValueError('Mando ausente, sin identidad estable o duplicado.')
            p=next(p for p in self.controllers.profiles() if p['id']==profile_id)
            game=self.installed.raw(game_id)
            self.controllers.bind(profile_id,scope,game_id,game['platform'] if game else '',p['engine'],device_id,family,player)
            self._message='Asociación guardada; se seleccionará al iniciar el juego.';self.operationChanged.emit();return True
        except (StopIteration,TypeError,OSError,ValueError,sqlite3.Error) as e:self._message='No se pudo asociar: '+str(e);self.operationChanged.emit();return False
    @Slot()
    def retryControllerRecovery(self):
        if self._profile!="adult" or self.launchBusy:return
        self.controllers.recovery=self.controllers.recover(confirmed_stopped=True)
        self._message=self.controllers.recovery
        journal=self.store.get('controller_restore_journal',{})
        if journal:self._message+=' Copia: '+journal.get('backup','')
        self.operationChanged.emit()
    @Slot(str,result=bool)
    def configureControllerTarget(self,url):
        if self._profile!="adult" or self.launchBusy:return False
        try:
            from .installed import local_path
            self.controllers.configure_target(str(local_path(url)))
            self._message='Destino guardado. La aplicación temporal requiere activación explícita.';self.operationChanged.emit();return True
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot()
    def toggleControllerAutoApply(self):
        if self._profile!='adult' or self.launchBusy:return
        self.store.set('controller_apply_enabled',not self.controllerAutoApply)
        self._message='Aplicación temporal: '+('activada' if self.controllerAutoApply else 'desactivada')+'. Se exige perfil completo sin índices SDL variables; se conserva una copia de seguridad.'
        self.operationChanged.emit()
    @Property(str,notify=operationChanged)
    def controllerLayout(self):return self.store.get("controller_layout","sony")
    @Slot()
    def toggleControllerLayout(self):
        self.store.set("controller_layout","standard" if self.controllerLayout=="sony" else "sony")
        self.operationChanged.emit()
    @Property(str,notify=libraryChanged)
    def librarySource(self):return self.store.get("library_source","real")
    @Property(str,notify=operationChanged)
    def operationMessage(self):return self._message if self._profile=="adult" else ""
    @Property(str,notify=operationChanged)
    def launchState(self):return self.launcher.state
    @Property(bool,notify=operationChanged)
    def launchBusy(self):return self.launcher.busy
    @Property("QVariantMap",notify=operationChanged)
    def pendingLaunch(self):return self.launcher.pending
    @Property("QVariantMap",notify=operationChanged)
    def pendingArtwork(self):return self.artwork.pending
    @Slot(str)
    def setLibrarySource(self,source):
        if source not in ["real","demo"]:return
        self.launcher.cancel();self.artwork.discard();self.metadata.pending=None
        self._detail_id="";self._focused_id="";self.store.set("library_source",source)
        self.libraryChanged.emit();self.indexChanged.emit();self.detailChanged.emit();self.visualChanged.emit()
    @Slot(str,str,str,result=bool)
    @Slot(str,str,str,str,result=bool)
    def importGame(self,name,platform,path,arguments="[]"):
        try:
            if self._profile!="adult":raise ValueError("Importación disponible en el perfil Adulto. Los títulos sin edad verificada no se muestran en Infantil.")
            game_id=self.installed.import_game(name,platform,path,arguments);self.setLibrarySource("real");self.clearFilters();self.focusItem(game_id)
            self._message="Juego importado. No se ejecutó ningún archivo.";self.operationChanged.emit();return True
        except (OSError,ValueError,sqlite3.Error) as e:
            self._message=str(e);self.operationChanged.emit();return False
    @Slot()
    def explainClose(self):
        self._message="El juego sigue ejecutándose. Ciérralo antes de salir de ORVEX.";self.operationChanged.emit()
    @Slot(str)
    def requestLaunch(self,item_id):
        if self._profile!="adult" or self.librarySource!="real":return
        self._message="";self.launcher.request(item_id)
    @Slot()
    def confirmLaunch(self):
        if self._profile=="adult" and self.librarySource=="real":self.launcher.confirm()
        else:self.launcher.cancel()
    @Slot()
    def cancelLaunch(self):self.launcher.cancel()
    @Slot(str,str,str,result=bool)
    def prepareArtwork(self,item_id,role,path):
        try:
            if self._profile!="adult":raise ValueError("Edición disponible en perfil Adulto.")
            self.artwork.prepare(item_id,role,path);self._message="Revisa la imagen antes de aplicarla. Usa solo recursos que tengas derecho a utilizar.";self.operationChanged.emit();return True
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot()
    def confirmArtwork(self):
        try:
            if self._profile!="adult":self.artwork.discard();return
            self.artwork.confirm();self._message="Imagen aplicada en la biblioteca personal."
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e)
        self.operationChanged.emit();self.refresh();self.detailChanged.emit()
    @Slot()
    def cancelArtwork(self):self.artwork.discard();self.operationChanged.emit()
    @Slot(str,str,result=bool)
    def associateControlProfile(self,item_id,path):
        if self._profile!="adult" or not self.installed.raw(item_id):return False
        profile=Path(path).expanduser()
        if not profile.is_absolute() or not profile.is_file() or profile.suffix.lower()!='.ini':
            self._message="Selecciona un perfil INI existente con ruta absoluta.";self.operationChanged.emit();return False
        self.store.set('control_profile:'+item_id,str(profile.resolve()))
        self._message="Asociación conservada. Activa ese perfil dentro del emulador; ORVEX no sobrescribe perfiles. Aplicación automática pendiente.";self.operationChanged.emit();return True
    @Slot(str,result="QVariantMap")
    def emulatorConfiguration(self,key):
        if self._profile!="adult" or key not in ("dolphin","pcsx2"):return {}
        return dict(executable=self.store.get(key+"_executable",""),root=self.store.get("rom_root",""))
    @Slot(str,str,str,result=bool)
    def configureEmulator(self,key,path,root):
        if self._profile!="adult" or key not in ['dolphin','pcsx2']:return False
        try:
            getattr(self,key).configure(path,root)
            if key=="dolphin":
                from ..controls.discovery import SDLInventory
                self.controller_inventory.close()
                self.controller_inventory=SDLInventory(self.store.get('dolphin_executable',''))
                self.controllers.inventory=self.controller_inventory
            self._message="Configuración guardada. Verifica BIOS y mandos dentro del emulador antes de jugar.";self.operationChanged.emit();return True
        except (OSError,ValueError) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot(str)
    def scanEmulator(self,key):
        if self._profile!="adult" or self.launchBusy or key not in ['dolphin','pcsx2']:return
        self._message="Escaneando…";self.operationChanged.emit()
        try:
            adapter=getattr(self,key);adapter.scan();r=adapter.result
            self._message=f"Encontrados: {r['found']} · Nuevos: {r['new']} · Existentes: {r['existing']} · Errores: {r['errors']}"
            self.refresh()
        except (OSError,ValueError,sqlite3.Error) as e:self._message="No se pudo escanear: "+str(e)
        self.operationChanged.emit()
    @Property("QVariantList",notify=operationChanged)
    def emulatorStatus(self):
        return [dict(name=key,configured=bool(self.store.get(key+'_executable',''))) for key in ['dolphin','pcsx2']]
    @Slot(str,str,result=bool)
    def configureDolphin(self,executable,root):
        if self._profile!="adult":return False
        try:self.dolphin.configure(executable,root);self._message="Dolphin configurado. No se ha iniciado ningún juego.";self.operationChanged.emit();return True
        except (OSError,ValueError) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot()
    def scanDolphin(self):
        if self._profile!="adult" or self.launchBusy:return
        try:self.scanEmulator("dolphin");self.scanEmulator("pcsx2");self.setLibrarySource("real");self.refresh()
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e)
        self.operationChanged.emit()
    @Property(bool,notify=operationChanged)
    def metadataPending(self):return self._profile=="adult" and self.metadata.pending is not None
    @Slot()
    def cancelMetadata(self):self.metadata.pending=None;self.operationChanged.emit()
    @Slot(str,str,result=str)
    def proposeMetadata(self,item_id,value):
        if self._profile!="adult" or self.launchBusy:return "Perfil u operación no autorizados"
        try:
            import json
            result=json.dumps(self.metadata.propose(item_id,value),ensure_ascii=False,indent=2)
        except (ValueError,TypeError) as e:result=str(e)
        self.operationChanged.emit();return result
    @Slot(result=bool)
    def confirmMetadata(self):
        if self._profile!="adult" or self.launchBusy or not self.metadataPending:return False
        try:
            self.metadata.confirm();self.refresh();self.operationChanged.emit();return True
        except (OSError,ValueError,sqlite3.Error) as e:self._message=str(e);self.operationChanged.emit();return False
    @Property("QVariantList",notify=libraryChanged)
    def managedGames(self):
        if self._profile!="adult":return []
        return [dict(self.installed.raw(e['id']),title=e['title']) for e in self.installed.games('adult',True)]
    @Slot(str,str,str,str,str,result=bool)
    def editGame(self,item_id,name,platform,path,args):
        if self._profile!="adult" or self.launchBusy:return False
        try:self.installed.edit(item_id,name,platform,path,args);self.refresh();return True
        except (ValueError,OSError,sqlite3.Error) as e:self._message=str(e);self.operationChanged.emit();return False
    @Slot(str,bool)
    def hideGame(self,item_id,hidden):
        if self._profile=="adult" and not self.launchBusy:self.installed.hide(item_id,hidden);self._detail_id="";self.refresh();self.detailChanged.emit()
    @Slot(str,bool)
    def removeGame(self,item_id,keep_history):
        if self._profile=="adult" and not self.launchBusy:self.installed.remove(item_id,keep_history);self._detail_id="";self.refresh();self.detailChanged.emit()
    @Property(str,notify=operationChanged)
    def diagnosticReport(self):
        import json
        if self._profile!="adult":return json.dumps(dict(version="0.4",message="Diagnóstico disponible en el perfil Adulto."),ensure_ascii=False)
        rows=self.store.db.execute("SELECT started_at,ended_at,duration_ms,status,exit_code FROM play_sessions ORDER BY id DESC LIMIT 100").fetchall()
        return json.dumps(dict(version="0.4",quick_menu=dict(state=self.quick_menu.state,message=self.quick_menu.message),controller=self.controllers.notice,input_error=self.controller_input_error,recovery=self.controllers.recovery,sessions=[dict(zip(['inicio','fin','duracion_ms','estado','codigo'],row)) for row in rows]),ensure_ascii=False,indent=2)
    def real_games(self):return self.installed.games(self._profile)
    def lookup(self,item_id):
        if item_id.startswith("local-"):return next((e for e in self.real_games() if e["id"]==item_id),{})
        return self.service.lookup(item_id,self._profile)
    def state(self):
        return self._states.setdefault((self._profile,self._page,self.librarySource),dict(query="",category="Todas",favorites=False,index=0))
    @Property(int, notify=pageChanged)
    def page(self):return self._page
    @Property(str, notify=libraryChanged)
    def profile(self):return self._profile
    @Property(str, notify=libraryChanged)
    def profileLabel(self):return "Infantil" if self._profile=="child" else "Adulto"
    @Property(str, notify=libraryChanged)
    def query(self):return self.state()["query"]
    @Property(str, notify=libraryChanged)
    def category(self):return self.state()["category"]
    @Property(bool, notify=libraryChanged)
    def favoritesOnly(self):return self.state()["favorites"]
    @Property(int, notify=indexChanged)
    def selectedIndex(self):return self.state()["index"]
    @Property("QVariantList", notify=libraryChanged)
    def options(self):
        if self._page==1 and self.librarySource=="real":return ["Todas"]+sorted({e["platform"] for e in self.real_games()})
        return self.service.options(self._profile,"media" if self._page==2 else "game")
    @Property("QVariantList", notify=libraryChanged)
    def entries(self):
        if self._page==0:
            return self.recentGames
        if self._page==3:return []
        s=self.state()
        if self._page==1 and self.librarySource=="real":
            return [e for e in self.real_games() if normalized(s["query"].strip()) in normalized(e["title"]) and (s["category"]=="Todas" or s["category"]==e["platform"]) and (not s["favorites"] or e["favorite"])]
        return self.service.query(self._profile,"media" if self._page==2 else "game",s["query"],s["category"],s["favorites"])
    @Property(bool, notify=detailChanged)
    def detailOpen(self):return bool(self._detail_id)
    @Property("QVariantMap", notify=detailChanged)
    def detail(self):return self.decorate(self.lookup(self._detail_id))
    def decorate(self, entry):
        return dict(entry,progress=presentation(self.progress_provider.get(self._profile,entry["id"]))) if entry and entry["kind"]=="game" and not entry.get("installed") else entry
    @Property("QVariantList", notify=libraryChanged)
    def recentGames(self):
        games=[self.decorate(e) for e in self.service.query(self._profile,"game")]
        return sorted([e for e in games if e["progress"].get("last_session")],key=lambda e:e["progress"]["last_session"],reverse=True)[:4]
    @Property("QVariantList", notify=libraryChanged)
    def showcase(self):
        items=[self.decorate(e) for e in self.entries]
        if self._page==1 and self.librarySource=="real":
            # Stable secondary ordering for never-played titles and equal timestamps.
            items.sort(key=lambda e:(normalized(e["title"]),e["id"]))
            items.sort(key=lambda e:e["progress"]["last_session"] or "",reverse=True)
        return items
    @Slot(str)
    def openTitle(self,item_id):
        if item_id in {e["id"] for e in self.showcase+self.entries}:
            self._detail_id=item_id;self.detailChanged.emit();self.visualChanged.emit()
    @Property("QVariantMap", notify=visualChanged)
    def featured(self):
        entry=self.lookup(self._focused_id)
        allowed_ids={e["id"] for e in self.showcase}
        return self.decorate(entry if entry and entry["id"] in allowed_ids else (self.showcase[0] if self.showcase else {}))
    @Property(str, notify=visualChanged)
    def backgroundMode(self):return self.store.get("background_mode","dynamic")
    @Property(str, notify=visualChanged)
    def fixedBackground(self):return self.store.get("background_fixed","aurora")
    @Property("QVariantList", notify=libraryChanged)
    def backgroundOptions(self):return [dict(id=e["id"],title=e["title"]) for e in self.service.visible(self._profile)]
    @Property(str, notify=visualChanged)
    def backgroundArt(self):
        if self.backgroundMode=="default":return ""
        if self.backgroundMode=="fixed":return self.service.lookup(self.fixedBackground,self._profile).get("art", "")
        return (self.detail if self.detailOpen else self.featured).get("art", "")
    @Property(str, notify=visualChanged)
    def backgroundUrl(self):
        from .artwork import resolve_art
        if self.librarySource=="real" and self._page==1 and self.backgroundMode=="dynamic":
            return (self.detail if self.detailOpen else self.featured).get("backdrop_url","")
        return resolve_art(self.backgroundArt,"backdrop")
    @Slot(str)
    def focusItem(self,item_id):
        if item_id in {e["id"] for e in self.entries+self.showcase} and item_id!=self._focused_id:
            self._focused_id=item_id;self.visualChanged.emit()
    @Slot(str)
    def setBackgroundMode(self,mode):
        if mode in ["dynamic","fixed","default"]:
            self.store.set("background_mode",mode);self.visualChanged.emit()
    @Slot(str)
    def setFixedBackground(self,item_id):
        if self.service.lookup(item_id,self._profile):
            self.store.set("background_fixed",item_id);self.visualChanged.emit()
    @Property(bool, notify=changed)
    def reducedMotion(self):return self.store.get("reduced_motion",False)
    @Slot()
    def toggleMotion(self):
        self.store.set("reduced_motion",not self.reducedMotion);self.changed.emit()
    @Slot(int)
    def navigate(self,page):
        if page not in range(4):return
        if page==0:page=1
        self._detail_id="";self._page=page
        self.pageChanged.emit();self.libraryChanged.emit();self.indexChanged.emit();self.visualChanged.emit();self.detailChanged.emit();self.visualChanged.emit()
    @Slot(str)
    def setProfile(self,profile):
        if profile not in PROFILES or profile==self._profile:return
        self.launcher.cancel();self.artwork.discard();self.metadata.pending=None
        self._profile=profile;self._detail_id="";self.store.set("profile",profile)
        self.operationChanged.emit()
        self.libraryChanged.emit();self.indexChanged.emit();self.visualChanged.emit();self.detailChanged.emit();self.visualChanged.emit()
    @Slot()
    def refresh(self):
        self.state()["index"]=min(self.state()["index"],max(0,len(self.entries)-1))
        self.libraryChanged.emit();self.indexChanged.emit();self.visualChanged.emit()
    @Slot(str)
    def setQuery(self,value):
        self.state()["query"]=value;self.state()["index"]=0;self.refresh()
    @Slot(str)
    def setCategory(self,value):
        if value not in self.options:return
        self.state()["category"]=value;self.state()["index"]=0;self.refresh()
    @Slot()
    def toggleFavorites(self):
        self.state()["favorites"]=not self.favoritesOnly;self.state()["index"]=0;self.refresh()
    @Slot()
    def clearFilters(self):
        for state in self._states.values():state.update(query="",category="Todas",favorites=False,index=0)
        self.refresh()
    @Slot(int)
    def selectIndex(self,index):
        if 0<=index<len(self.entries) and index!=self.selectedIndex:
            self.state()["index"]=index;self.indexChanged.emit();self.visualChanged.emit()
    @Slot(int)
    def openDetail(self,index):
        if 0<=index<len(self.entries):
            self.selectIndex(index);self._detail_id=self.entries[index]["id"];self.detailChanged.emit();self.visualChanged.emit()
    @Slot()
    def closeDetail(self):
        self._detail_id="";self.detailChanged.emit();self.visualChanged.emit()
    @Slot(str)
    def toggleFavorite(self,item_id):
        if item_id.startswith("local-") and self.lookup(item_id):
            self.store.set_favorite(self._profile,item_id,item_id not in self.store.favorites(self._profile));self.refresh();self.detailChanged.emit()
        elif self.service.toggle_favorite(item_id,self._profile):
            self.refresh();self.detailChanged.emit();self.visualChanged.emit()
