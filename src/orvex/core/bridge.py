from PySide6.QtCore import QObject, Property, Signal, Slot
from .store import catalog
from .library import LibraryService, PROFILES

class Bridge(QObject):
    changed = Signal()
    libraryChanged = Signal()
    pageChanged = Signal()
    detailChanged = Signal()
    indexChanged = Signal()
    def __init__(self, store):
        super().__init__()
        self.store=store
        self.service=LibraryService(store)
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
            return self.service.query(self._profile)[:4]
        if self._page==3:return []
        s=self.state()
        return self.service.query(self._profile,"media" if self._page==2 else "game",s["query"],s["category"],s["favorites"])
    @Property(bool, notify=detailChanged)
    def detailOpen(self):return bool(self._detail_id)
    @Property("QVariantMap", notify=detailChanged)
    def detail(self):return self.service.lookup(self._detail_id,self._profile)
    @Property(bool, notify=changed)
    def reducedMotion(self):return self.store.get("reduced_motion",False)
    @Slot()
    def toggleMotion(self):
        self.store.set("reduced_motion",not self.reducedMotion);self.changed.emit()
    @Slot(int)
    def navigate(self,page):
        if page not in range(4):return
        self._detail_id="";self._page=page
        self.pageChanged.emit();self.libraryChanged.emit();self.indexChanged.emit();self.detailChanged.emit()
    @Slot(str)
    def setProfile(self,profile):
        if profile not in PROFILES or profile==self._profile:return
        self._profile=profile;self._detail_id="";self.store.set("profile",profile)
        self.libraryChanged.emit();self.indexChanged.emit();self.detailChanged.emit()
    def refresh(self):
        self.state()["index"]=min(self.state()["index"],max(0,len(self.entries)-1))
        self.libraryChanged.emit();self.indexChanged.emit()
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
            self.state()["index"]=index;self.indexChanged.emit()
    @Slot(int)
    def openDetail(self,index):
        if 0<=index<len(self.entries):
            self.selectIndex(index);self._detail_id=self.entries[index]["id"];self.detailChanged.emit()
    @Slot()
    def closeDetail(self):
        self._detail_id="";self.detailChanged.emit()
    @Slot(str)
    def toggleFavorite(self,item_id):
        if self.service.toggle_favorite(item_id,self._profile):
            self.refresh();self.detailChanged.emit()
