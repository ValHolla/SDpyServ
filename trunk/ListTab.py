
import gtk
import gobject
from threading import Thread

class ListTab(Thread):
    def ListTreeSelection_cb(self, path, userdata=None):
        SelectedIter=self.ListTreeModel.get_iter(path)
        SelectedValue=self.ListTreeModel.get_value(SelectedIter,0)
        delButton=self.builder.get_object('btnDelList')
        SelectedValueID=self.dbc.dbFetchRow("""
        select list_id from list_names where list_name = %s
        """ , (SelectedValue))
        refreshButton=self.builder.get_object('btnRefreshList')
        dirAddButton=self.builder.get_object('btnFileLocationAdd')
        ## Clear the Folder Tree
        self.FolderTreeModel.clear()
        ## Repopulate with folders for selected list only
        FolderNames=self.dbc.dbFetchAll("""
        select list_dirs.dir_name, list_name_dir.dir_recurse_bool 
        from list_dirs, list_name_dir
        where list_name_dir.list_id = %s
        and list_name_dir.list_dir_id = list_dirs.list_dir_id
        """, (SelectedValueID))
        if (FolderNames):
            for Name in FolderNames:
                self.PushFolderGUI(Name["dir_name"],Name["dir_recurse_bool"])
        delButton.set_sensitive(True)
        refreshButton.set_sensitive(True)
        dirAddButton.set_sensitive(True)
        return True

    def FolderTreeSelection_cb(self, path, userdata=None):
        return True

    def FolderTreeRecurseToggled_cb(self, cell, path, model):
        ListSelection=self.ListTreeView.get_selection()
        (TreeModel, listIter) = ListSelection.get_selected()
        ListSelected=TreeModel.get_value(listIter,0)
        ListSelectedID=self.dbc.dbFetchRow("""
        select list_id from list_names where list_name = %s
        """, (ListSelected))
        SelectedIter=model.get_iter(path)
        SelectedValue=model.get_value(SelectedIter,0)
        SelectedValueID=self.dbc.dbFetchRow("""
        select list_dir_id from list_dirs where dir_name = %s
        """ , (SelectedValue))
        if (not model[path][1]):
            self.dbc.dbUpdateRow("""
            update list_name_dir set dir_recurse_bool = 1
            where list_dir_id = %s and list_id = %s
            """, (SelectedValueID, ListSelectedID))
        else:
            self.dbc.dbUpdateRow("""
            update list_name_dir set dir_recurse_bool = 0
            where list_dir_id = %s and list_id = %s
            """, (SelectedValueID, ListSelectedID))
        model[path][1] = not model[path][1]
        pass
        
    def BuildTreeView(self):
        self.ListTreeView=self.builder.get_object('ListFrameTree')
        self.ListTreeModel=gtk.ListStore(gobject.TYPE_STRING)
        self.ListTreeView.set_model(self.ListTreeModel)
        self.ListTreeView.set_headers_visible(True)
        self.ListTreeSelection=self.ListTreeView.get_selection()
        ListTreeRender=gtk.CellRendererText()
        ListTreeColumn=gtk.TreeViewColumn("List Name", ListTreeRender, text=0)
        gtk.TreeViewColumn.set_sizing(ListTreeColumn, 'GTK_TREE_VIEW_COLUMN_FIXED')
        ListTreeColumn.set_resizable(False)
        self.ListTreeView.append_column(ListTreeColumn)
        self.ListTreeSelection.set_select_function(self.ListTreeSelection_cb, self)
        self.ListTreeView.show_all()

    def BuildFolderView(self):
        self.FolderTreeView=self.builder.get_object('FileLocationTree')
        self.FolderTreeModel=gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_BOOLEAN)
        self.FolderTreeView.set_model(self.FolderTreeModel)
        self.FolderTreeView.set_headers_visible(True)
        self.FolderTreeSelection=self.FolderTreeView.get_selection()
        self.FolderTreeSelection.set_mode(gtk.SELECTION_SINGLE)
        FolderTreeRender=gtk.CellRendererText()
        FolderColumnRender=gtk.CellRendererToggle()
        
        FolderTreeColumn=gtk.TreeViewColumn("Folders", FolderTreeRender, text=0)
        gtk.TreeViewColumn.set_sizing(FolderTreeColumn, 'GTK_TREE_VIEW_COLUMN_FIXED')
        gtk.TreeViewColumn.set_fixed_width(FolderTreeColumn, 300)
        FolderTreeColumn.set_resizable(False)
        
        FolderRecurseColumn=gtk.TreeViewColumn("Recurse", FolderColumnRender)
        FolderColumnRender.set_property('activatable', True)
        FolderColumnRender.connect( 'toggled', self.FolderTreeRecurseToggled_cb, self.FolderTreeModel)
        FolderRecurseColumn.add_attribute(FolderColumnRender,"active", 1)
        gtk.TreeViewColumn.set_sizing(FolderRecurseColumn, 'GTK_TREE_VIEW_COLUMN_FIXED')
        FolderRecurseColumn.set_resizable(False)
        
        self.FolderTreeView.append_column(FolderTreeColumn)
        self.FolderTreeView.append_column(FolderRecurseColumn)
        self.FolderTreeSelection.set_select_function(self.FolderTreeSelection_cb, self.FolderTreeModel)
        self.FolderTreeView.show_all()
        
    def PushListGUI(self,ListName):
        listIter=self.ListTreeModel.insert_before(None,None)
        self.ListTreeModel.set_value(listIter,0,ListName)
        return listIter

    def PushFolderGUI(self,FolderName,Recurse):
        Found = self.FolderTreeModel.get_iter_first()
        while (Found != None):
            if (FolderName == self.FolderTreeModel.get_value(Found, 0)):
                return False
            else:
                Found = self.FolderTreeModel.iter_next(Found)

        folderIter=self.FolderTreeModel.insert_before(None,None)
        self.FolderTreeModel.set_value(folderIter,0,FolderName)
        if (Recurse):
            self.FolderTreeModel.set_value(folderIter,1,True)
        else:
            self.FolderTreeModel.set_value(folderIter,1,False)
        dirDelButton=self.builder.get_object('btnFileLocationDelete')
        if (self.FolderTreeModel):
            if (len(self.FolderTreeModel) > 1):
                dirDelButton.set_sensitive(True)
            else:
                dirDelButton.set_sensitive(False)
        return folderIter

    def InitListTab(self):
        """
        Populate the List Tab with Default/Saved Values
        """
        ListNames=self.dbc.dbFetchAll("""
        select list_name from list_names
        """)
        if (ListNames):
            for Name in ListNames:
                self.PushListGUI(Name["list_name"])
                                      
    def __init__(self, builder, dbc):
        Thread.__init__(self)
        self.builder=builder
        self.dbc=dbc
        self.ListTreeView=None
        self.ListTreeModel=None
        self.ListTreeSelection=None
        self.FolderTreeView=None
        self.FolderTreeModel=None
        self.FolderTreeSelection=None
        self.BuildTreeView()
        self.BuildFolderView()
        self.InitListTab()
