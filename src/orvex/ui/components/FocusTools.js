.pragma library
function controls(root) {
    var result=[]
    function visit(item) {
        if(!item || !item.visible || !item.enabled)return
        if(item.activeFocusOnTab && item.width>0 && item.height>0) {result.push(item);return}
        var children=item.children || []
        for(var i=0;i<children.length;i++)visit(children[i])
    }
    visit(root);return result
}
function move(root,current,forward) {
    var items=controls(root)
    if(!items.length)return false
    var i=items.indexOf(current)
    var next=items[(i+(forward?1:items.length-1)+items.length)%items.length]
    next.forceActiveFocus(Qt.TabFocusReason)
    return true
}
function first(root) {var items=controls(root);if(items.length)items[0].forceActiveFocus()}
