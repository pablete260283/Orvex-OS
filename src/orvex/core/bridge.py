from PySide6.QtCore import QObject, Property, Signal, Slot
from .store import catalog
from .progress import DemoProgressProvider, presentation
from .library import LibraryService, PROFILES

class Bridge(QObject):
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
        self._page=0
        self._profile=store.get("profile","adult")
        if self._profile not in PROFILES:self._profile="adult"
        self._states={}
        self._detail_id=""
    def state(self):
        return self._states.setdefault((self._profile,self._page),dict(query="",category="Todas",favorites=False,index=0))
    @Property("QVariantList", constant=True)
    def catalog(self):
        # Historical demo-data contract; views use the profile-filtered entries API.
        return catalog()
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
    def options(self):return self.service.options(self._profile,"media" if self._page==2 else "game")
    @Property("QVariantList", notify=libraryChanged)
    def entries(self):
        if self._page==0:
            return self.recentGames
        if self._page==3:return []
        s=self.state()
        return self.service.query(self._profile,"media" if self._page==2 else "game",s["query"],s["category"],s["favorites"])
    @Property(bool, notify=detailChanged)
    def detailOpen(self):return bool(self._detail_id)
    @Property("QVariantMap", notify=detailChanged)
    def detail(self):return self.decorate(self.service.lookup(self._detail_id,self._profile))
    def decorate(self, entry):
        return dict(entry,progress=presentation(self.progress_provider.get(self._profile,entry["id"]))) if entry and entry["kind"]=="game" else entry
    @Property("QVariantList", notify=libraryChanged)
    def recentGames(self):
        games=[self.decorate(e) for e in self.service.query(self._profile,"game")]
        return sorted([e for e in games if e["progress"].get("last_session")],key=lambda e:e["progress"]["last_session"],reverse=True)[:4]
    @Property("QVariantMap", notify=visualChanged)
    def featured(self):
        entry=self.service.lookup(self._focused_id,self._profile)
        allowed_ids={e["id"] for e in self.entries}
        return self.decorate(entry if entry and entry["id"] in allowed_ids else (self.entries[0] if self.entries else {}))
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
    @Slot(str)
    def focusItem(self,item_id):
        if item_id in {e["id"] for e in self.entries} and item_id!=self._focused_id:
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
        self._detail_id="";self._page=page
        self.pageChanged.emit();self.libraryChanged.emit();self.indexChanged.emit();self.visualChanged.emit();self.detailChanged.emit();self.visualChanged.emit()
    @Slot(str)
    def setProfile(self,profile):
        if profile not in PROFILES or profile==self._profile:return
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
        if self.service.toggle_favorite(item_id,self._profile):
            self.refresh();self.detailChanged.emit();self.visualChanged.emit()
