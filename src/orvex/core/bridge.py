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
        self.installed=InstalledLibrary(store)
        self.launcher=GameLauncher(self.installed,self)
        self._temp_assets=tempfile.TemporaryDirectory(prefix="orvex-assets-") if store.path is None else None
        if self._temp_assets:weakref.finalize(self,self._temp_assets.cleanup)
        root=Path(self._temp_assets.name) if self._temp_assets else store.path.parent/"artwork"
        self.artwork=LocalArtwork(self.installed,root)
        self._message=""
        self.launcher.changed.connect(self._launch_updated)
    def _launch_updated(self):
        self._message=self.launcher.message;self.operationChanged.emit();self.refresh();self.detailChanged.emit()
    @Property(str,notify=libraryChanged)
    def librarySource(self):return self.store.get("library_source","real")
    @Property(str,notify=operationChanged)
    def operationMessage(self):return self._message
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
        self.launcher.cancel();self.artwork.discard()
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
        if self._page==2:return self.service.query(self._profile,"media")[:8]
        if self.librarySource=="real":return sorted(self.real_games(),key=lambda e:e["progress"]["last_session"] or "",reverse=True)[:8]
        return self.recentGames or [self.decorate(e) for e in self.service.query(self._profile,"game")]
    @Slot(str)
    def openTitle(self,item_id):
        if item_id in {e["id"] for e in self.showcase+self.entries}:
            self._detail_id=item_id;self.detailChanged.emit();self.visualChanged.emit()
    @Property("QVariantMap", notify=visualChanged)
    def featured(self):
        entry=self.lookup(self._focused_id)
        allowed_ids={e["id"] for e in self.entries+self.showcase}
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
        self.launcher.cancel();self.artwork.discard()
        self._profile=profile;self._detail_id="";self.store.set("profile",profile)
        self.libraryChanged.emit();self.indexChanged.emit();self.visualChanged.emit();self.detailChanged.emit();self.visualChanged.emit()
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
