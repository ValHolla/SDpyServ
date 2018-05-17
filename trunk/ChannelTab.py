
import gtk, gobject
from threading import Thread
        
class ChannelTab(Thread):
    
    def ChannelTreeSelection_cb(self, path, userdata=None):
        Iter=self.ChannelTreeModel.get_iter(path)
        Network=self.ChannelTreeModel.get_value(Iter,0)
        Channel=self.ChannelTreeModel.get_value(Iter,1)
        self.ChannelDetailModel.clear()
        self.PushChannelDetails(Network,Channel)
        self.builder.get_object('btnDelChannel').set_sensitive(True)
        self.builder.get_object('btnEditChannel').set_sensitive(False)
        self.builder.get_object('ChannelDetailDelBtn').set_sensitive(False)
        self.builder.get_object('BuildListBtn').set_sensitive(False)
        return True
        
    def ChannelDetailSelection_cb(self, path, userdata=None):
        (Model,Iter)=self.ChannelTreeSelection.get_selected()
        Network=Model.get_value(Iter,0)
        Channel=Model.get_value(Iter,1)
        self.builder.get_object('btnEditChannel').set_sensitive(True)
        self.builder.get_object('BuildListBtn').set_sensitive(True)
        Values=self.dbc.dbFetchAll('''
        select distinct
            N.nick_name as Nick, L.list_name as List,
            C.ad_frequency as Freq,
            C.text_before_ad_bool as AdCheck,
            C.text_before_rand_bool as RandCheck
        from
            serving_nicks N, list_names L, channels C, networks W
        where
            C.channel_name = %s and
            N.nick_id = C.nick_id and
            W.network_id = C.network_id and
            L.list_id = C.list_id and
            W.network_name = %s
            ''', (Channel, Network))

        if (len(Values) > 1):
            self.builder.get_object('ChannelDetailDelBtn').set_sensitive(True)
        else:
            self.builder.get_object('ChannelDetailDelBtn').set_sensitive(False)
        return True
         
    def BuildChannelView(self):
        TreeView=self.builder.get_object('ChannelTree')
        TreeModel=gtk.ListStore(gobject.TYPE_STRING, \
                                        gobject.TYPE_STRING)
        TreeView.set_model(TreeModel)
        TreeSelection=TreeView.get_selection()
        TreeRenderer=gtk.CellRendererText()
        NetworkColumn=gtk.TreeViewColumn\
                ("Network", TreeRenderer, text=0)
        ChannelColumn=gtk.TreeViewColumn\
                ("Channel", TreeRenderer, text=1)
        gtk.TreeViewColumn.set_sizing\
                (NetworkColumn, 'GTK_TREE_VIEW_COLUMN_FIXED')
        gtk.TreeViewColumn.set_sizing\
                (ChannelColumn, 'GTK_TREE_VIEW_COLUMN_FIXED')
        ChannelColumn.set_expand(True)
        gtk.TreeViewColumn.set_fixed_width(NetworkColumn, 150)
        NetworkColumn.set_resizable(True)
        ChannelColumn.set_resizable(True)
        TreeView.append_column(NetworkColumn)
        TreeView.append_column(ChannelColumn)
        TreeSelection.set_select_function\
                (self.ChannelTreeSelection_cb, self)
        TreeView.show_all()
        return (TreeView,TreeModel,TreeSelection)
    
    def BuildChannelDetails(self):
        ## ('Column Name', 'Header Text', 'Size', 'Resizable')
        columnNames = [('NickColumn','Nick','175', True),
                       ('ListNameColumn','List To Serve','175', True),
                       ('AdTimeColumn','Ad Show','70', False),
                       ('AdTextColumn','B4 Ad','50', False),
                       ('RandTextColumn','B4 Random','70', False)]
            
        DetailModel=gtk.ListStore(gobject.TYPE_STRING, \
                                  gobject.TYPE_STRING, \
                                  gobject.TYPE_STRING, \
                                  gobject.TYPE_STRING, \
                                  gobject.TYPE_STRING)
            
        DetailView=self.builder.get_object('ChannelDetailTree')
        DetailView.set_model(DetailModel)
        DetailSelection=DetailView.get_selection()
        TreeRenderer=gtk.CellRendererText()
            
        for i in range(len(columnNames)):
            (column, title, width, resize)=columnNames[i]
            column=gtk.TreeViewColumn(title, TreeRenderer, text=i)
            gtk.TreeViewColumn.set_sizing(column, 'GTK_TREE_VIEW_COLUMN_FIXED')
            gtk.TreeViewColumn.set_fixed_width(column, int(width))
            column.set_resizable(resize)
            DetailView.append_column(column)
                
        DetailSelection.set_select_function\
                (self.ChannelDetailSelection_cb, self)
        DetailView.show_all()
        return (DetailView,DetailModel,DetailSelection)

    def BuildListCombo(self,ComboName):
        ComboBox=self.builder.get_object(ComboName)
        ComboModel=gtk.ListStore(gobject.TYPE_STRING)
        ComboBox.set_model(ComboModel)
        ComboCell = gtk.CellRendererText()
        ComboBox.pack_start(ComboCell, True)
        ComboBox.add_attribute(ComboCell, 'text', 0)
        ComboBox.show_all()
        return (ComboBox,ComboModel)
    
    def InitializeNewListCombo(self, Model):
        try:
            Model.clear()
        except:
            pass
        Names=self.dbc.dbFetchAll('''
        select list_name from list_names''')
        try:
            for key in Names:
                comboIter=Model.insert_before(None, None)
                Model.set_value(comboIter,0,key["list_name"])
        except TypeError, e:
            pass  ## Nothing there to Initialize

    def InitializeChannelTree(self):
        try:
            self.ChannelTreeModel.clear()
        except:
            pass
        Values=self.dbc.dbFetchAll('''
        select distinct N.network_name as Network, C.channel_name as Channel
        from networks N, channels C
        where N.network_id = C.network_id''')
        try:
            for Value in Values:
                self.PushChannelGui(Value["Network"], Value["Channel"])
        except TypeError, e:
            pass ## Nothing to Initialize

        ButtonChannelAdd = self.builder.get_object('btnAddChannel')
        listNum=self.dbc.dbFetchRow('''
        select count(list_id) from list_names''')
        if (listNum > 0):
            ButtonChannelAdd.set_sensitive(True)
        else:
            ButtonChannelAdd.set_sensitive(False)

        
    def PushListCombo(self,Model,ListName):
        comboIter=Model.insert_before(None,None)
        Model.set_value(comboIter,0,ListName)

    def PushChannelGui(self,Network,Channel):
        Found=self.ChannelTreeModel.get_iter_first()
        while (Found != None):
            if (Network == self.ChannelTreeModel.get_value(Found, 0) and
                    Channel == self.ChannelTreeModel.get_value(Found, 1)):
                return False
            else:
                Found = self.ChannelTreeModel.iter_next(Found)

        Iter=self.ChannelTreeModel.insert_before(None,None)
        self.ChannelTreeModel.set_value(Iter,0,Network)
        self.ChannelTreeModel.set_value(Iter,1,Channel)


    def PushChannelDetails(self,Network,Channel):
        NetworkID=self.dbc.dbFetchRow('''
        select network_id from networks where network_name = %s
        ''', (Network))
        Values=self.dbc.dbFetchAll('''
        select distinct
            N.nick_name as Nick, L.list_name as List,
            C.ad_frequency as Freq,
            C.text_before_ad_bool as AdCheck,
            C.text_before_rand_bool as RandCheck
        from
            serving_nicks N, list_names L, channels C, networks W
        where
            C.channel_name = %s and
            N.nick_id = C.nick_id and
            W.network_id = C.network_id and
            L.list_id = C.list_id and
            W.network_name = %s
            ''', (Channel, Network))

        if (len(Values) > 1):
            self.builder.get_object('ChannelDetailDelBtn').set_sensitive(True)
        else:
            self.builder.get_object('ChannelDetailDelBtn').set_sensitive(False)

        for Value in Values:
            Iter=self.ChannelDetailModel.insert_before(None,None)
            self.ChannelDetailModel.set_value(Iter,0,Value["Nick"])
            self.ChannelDetailModel.set_value(Iter,1,Value["List"])
            self.ChannelDetailModel.set_value(Iter,2,Value["Freq"])
            if (Value["AdCheck"] == 1):
                self.ChannelDetailModel.set_value(Iter,3,'True')
            else:
                self.ChannelDetailModel.set_value(Iter,3,'False')
            if (Value["RandCheck"] == 1):
                self.ChannelDetailModel.set_value(Iter,4,'True')
            else:
                self.ChannelDetailModel.set_value(Iter,4,'False')
        
    def BuildList(self):
        ProgressLabel=self.builder.get_object('BuildListProgressLbl')
        ProgressBar=self.builder.get_object('BuildListProgress')
        ProgressButton=self.builder.get_object('BuildListProgressBtn')
        gtk.gdk.threads_enter()
        ProgressButton.set_label('gtk-cancel')
        gtk.gdk.threads_leave()
        
        FileInfo = "Info Place Holder"
        (dModel,dIter)=self.channelTab.ChannelDetailSelection.get_selected()
        NickName=dModel.get_value(dIter,0)
        ListName=dModel.get_value(dIter,1)
        ListDate=time.strftime("%Y%m%d")
        filename=string.join((\
                string.join((NickName,ListName,ListDate),'-'),'txt'),'.')
        ServDir = self.dbc.dbFetchRow('''
                    select serving_directory from options''')
        if (not ServDir):
            ServDir = os.path.join(os.path.expanduser("~"),'.xchat2','SDpyServ')

        if (not os.path.exists(ServDir)):
            os.mkdirs(ServDir,0755)
        elif (not os.path.isdir(ServDir)):
            os.unlink(ServDir)
            os.mkdirs(ServDir,0755)

        filePath = os.path.join(ServDir,filename)
        gtk.gdk.threads_enter()
        ProgressLabel.set_text(u'List: %s' % (filePath))
        gtk.gdk.threads_leave()

        ListCnt = self.dbc.dbFetchRow('''
                    select count(file_id) from list_contents''')

        ListFiles = self.dbc.dbFetchAll('''
                    select F.file_name from file F, list_contents L
                    where F.file_id = L.file_id''')
        try:
            oFile = open(filePath,'w')
        except IOError, e:
            self.sdError.UserError('Can Not open file for writing')

        if (ListCnt == 0):
            ListCnt += 1
        fileCnt = 1
        for file in ListFiles:
            oFile.write('!' + NickName + ' ' + file["file_name"] +
                    ' ::INFO:: ' + FileInfo + '\n')
            gtk.gdk.threads_enter()
            ProgressBar.setfraction(fileCnt / ListCnt)
            gtk.gdk.threads_leave()
            if (fileCnt < ListCnt):
                fileCnt += 1
        oFile.close()

        toZip = self.dbc.dbFetchRow('''
                    select zip_lists_bool from options''')
        if (toZip == 1):
            try:
                zFile=zipfile.ZipFile(filePath + '.zip', 'w')
            except IOError, e:
                self.sdError.UserError('Can not open file for writing')

            zFile.write(filePath, os.path.basename(filePath), zipfile.ZIP_DEFLATED)
            zFile.close()
            try:
                os.unlink(filePath)
            except OSError, e:
                self.sdError.UserError('Can not remove text file')

    def __init__(self, builder, dbc):
        Thread.__init__(self)
        self.builder=builder
        self.dbc=dbc
        (self.ChannelTreeView,self.ChannelTreeModel,\
                 self.ChannelTreeSelection)=self.BuildChannelView()
        (self.ChannelDetailView,self.ChannelDetailModel,\
                 self.ChannelDetailSelection)=self.BuildChannelDetails()
        (self.NewComboBox,self.NewComboModel)=\
                self.BuildListCombo('NewListCombo')
        (self.EditComboBox,self.EditComboModel)=\
                self.BuildListCombo('EditListCombo')
        self.InitializeNewListCombo(self.NewComboModel)
        self.InitializeNewListCombo(self.EditComboModel)
        self.InitializeChannelTree()

