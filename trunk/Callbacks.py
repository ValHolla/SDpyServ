from GenerateList import GenerateList
from BuildList import BuildList
from threading import Thread, Event
import MySQLdb
import sys, os 
import gtk, gobject

class Callbacks(Thread):
## Global Window Callbacks
    def on_window_destroy(self, widget, userdata=None):
        gtk.main_quit()

    def BtnAbout_clicked_cb(self, widget, userdata=None):
        AboutWin=self.builder.get_object('AboutWindow')
        AboutWin.show_all()

    def AboutWindow_response_cb(self, widget, userdata=None):
        AboutWin=self.builder.get_object('AboutWindow')
        AboutWin.hide()

    def on_btnOk_clicked(self, widget, userdata=None):
        ## Main Tab Values
        for key in self.GuiOptions:
            try:
                self.GuiOptions[key]=self.builder.get_object(key).get_text()
            except AttributeError, e:
                '''RadioButtons and CheckBoxes do not have get_text()
                They are handeled with their own callbacks'''
                pass

        self.dbc.dbUpdateRow('''update priority set
        server_priority = %s, priority_extentions = %s''',
        (self.GuiOptions["ServerPriority"], 
        self.GuiOptions["ExtentionEntry"]))

        ## Options Tab values
        self.dbc.dbUpdateRow('''update options set 
           serving_directory = %s,
           send_slots_num = %s, dynamic_slots_num = %s, 
           queue_nick_num = %s, queue_full_num = %s, 
           max_find_results = %s, sm_file_low_cps = %s, 
           lg_file_low_cps = %s, lg_file_size_mb = %s, 
           max_list_queue = %s, ctcp_send_freq = %s, 
           rndm_play_freq = %s, queue_list_bool = %s, 
           send_ctcp_bool = %s, rndm_play_bool = %s, 
           enable_find_bool = %s, zip_lists_bool = %s, 
           log_option = %s ''', (self.GuiOptions["ServingDirectory"], 
                                self.GuiOptions["SendSlots"],
                                self.GuiOptions["DynamicSlots"], 
                                self.GuiOptions["FilesInQueue"],
                                self.GuiOptions["QueueFull"], 
                                self.GuiOptions["MaxFindNum"],
                                self.GuiOptions["SmallLowCps"], 
                                self.GuiOptions["LargeLowCps"],
                                self.GuiOptions["LargeFileSize"], 
                                self.GuiOptions["MaxListQueue"], 
                                self.GuiOptions["SendCtcpFreq"], 
                                self.GuiOptions["RandomPlayFreq"],
                                self.GuiOptions["QueueListCheck"],
                                self.GuiOptions["SendCtcpCheck"],
                                self.GuiOptions["RandomPlayCheck"],
                                self.GuiOptions["EnableFindCheck"], 
                                self.GuiOptions["ZipListCheck"],
                                self.GuiOptions["radioLogging"]))
        gtk.main_quit()

## Main Tab Callbacks
    def PriorityRadioToggle_cb(self, widget, userdata=None):
        radioPri = self.builder.get_object(widget.name)
        if (radioPri.get_active()):
            self.GuiOptions['ServerPriority']=self.PriorityList[widget.name]
    
    def ServingDirectoryChooser_current_folder_changed_cb(self, widget, userdata=None):
        Dir=widget.get_filename()
        self.GuiOptions["ServingDirectory"] = Dir
        self.dbc.dbUpdateRow('''
        update options set serving_directory = %s
        ''', Dir)

## Options Tab Callbacks
    def SendCtcpCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.GuiOptions['SendCtcpCheck'] = 1
            self.builder.get_object('SendCtcpFreq').set_sensitive(True)
        else:
            self.GuiOptions['SendCtcpCheck'] = 0
            self.builder.get_object('SendCtcpFreq').set_sensitive(False)

    def RandomPlayCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.GuiOptions['RandomPlayCheck'] = 1
            self.builder.get_object('RandomPlayFreq').set_sensitive(True)
            self.builder.get_object('NewBeforeRandomCheck').set_sensitive(True)
            self.builder.get_object('EditBeforeRandomCheck').set_sensitive(True)
        else:
            self.GuiOptions['RandomPlayCheck'] = 0
            self.builder.get_object('RandomPlayFreq').set_sensitive(False)
            self.builder.get_object('NewBeforeRandomCheck').set_sensitive(False)
            self.builder.get_object('EditBeforeRandomCheck').set_sensitive(False)
            self.dbc.dbUpdateRow("""
            update channels set text_before_rand_bool=0, text_before_rand = ''""")
            self.channelTab.ChannelDetailModel.clear()
            self.builder.get_object('btnEditChannel').set_sensitive(False)
            self.builder.get_object('ChannelDetailDelBtn').set_sensitive(False)
            self.builder.get_object('BuildListBtn').set_sensitive(False)
            self.channelTab.InitializeChannelTree()

    def QueueListCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.GuiOptions['QueueListCheck'] = 1
            self.builder.get_object('MaxListQueue').set_sensitive(True)
        else:
            self.GuiOptions['QueueListCheck'] = 0
            self.builder.get_object('MaxListQueue').set_sensitive(False)

    def LoggingRadioToggle_cb(self, widget, userdata=None):
        radioLog = self.builder.get_object(widget.name)
        if (radioLog.get_active()):
            self.GuiOptions['radioLogging']=self.LoggingList[widget.name]

    def EnableFindCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.GuiOptions['EnableFindCheck'] = 1
            self.builder.get_object('MaxFindNum').set_sensitive(True)
        else:
            self.GuiOptions['EnableFindCheck'] = 0
            self.builder.get_object('MaxFindNum').set_sensitive(False)

    def ZipListCheck_toggled_cb(self, widget, userdata=None):
        zipcheck = self.builder.get_object('ZipListCheck')
        if (zipcheck.get_active()):
            self.GuiOptions['ZipListCheck'] = 1
        else:
            self.GuiOptions['ZipListCheck'] = 0

## List Tab Callbacks
    def ProgressWindow_destroy_cb(self, widget, userdata=None):
        Progress=self.builder.get_object('ProgressWindow')
        Progress.hide()

    def ProgressButton_clicked_cb(self, widget, userdata=None):
        self.ProgressEvent.set()
        Progress=self.builder.get_object('ProgressWindow')
        Progress.hide()

    def on_btnRefreshList_clicked(self, widget, userdata=None):
        ListSelection=self.listTab.ListTreeView.get_selection()
        (TreeModel, listIter) = ListSelection.get_selected()
        ListSelected=TreeModel.get_value(listIter,0)
        Progress=self.builder.get_object('ProgressWindow')
        Progress.show_all()
        GenThread = Thread(target=GenerateList, \
                     args=(self.builder, self.dbc, \
                     ListSelected, self.ProgressEvent))
        GenThread.start()
        
    def on_btnDelList_clicked(self, widget, userdata=None):
        ListDeleteButton=self.builder.get_object('btnDelList')
        RefreshListButton=self.builder.get_object('btnRefreshList')
        FileDeleteButton=self.builder.get_object('btnFileLocationDelete')
        FileAddButton=self.builder.get_object('btnFileLocationAdd')
        ListSelection=self.listTab.ListTreeView.get_selection()
        ButtonChannelAdd=self.builder.get_object('btnAddChannel')
        (TreeModel, listIter) = ListSelection.get_selected()
        ListSelected=TreeModel.get_value(listIter,0)
        ListID=self.dbc.dbFetchRow("""
        select list_id from list_names where list_name = %s
        """ , (ListSelected))
        ListNameDirSaved = self.dbc.dbFetchAll("""
        select list_dir_id, list_id, dir_recurse_bool
        from list_name_dir where list_id = %s
        """, (ListID))
        
        ListCount = self.dbc.dbFetchRow("""
        select count(*) from channels where list_id = %s
        """, (ListID))

        if (int(ListCount) < 1):
            ## Remove folder/list associations
            self.dbc.dbDeleteRow("""
            delete from list_name_dir where list_id = %s
            """, (ListID))
            ## remove any newly unused folders
            self.dbc.dbDeleteRow("""
            delete from list_name_dir where list_id = %s
            """, (ListID))
            self.dbc.dbDeleteRow("""
            delete from list_contents where list_id = %s
            """, (ListID))
            self.dbc.dbDeleteRow("""
            delete from list_dirs where list_dir_id not in
            (select list_dir_id from list_name_dir)
            """)
            ## Remove List from DB
            self.dbc.dbDeleteRow("""
            delete from list_names where list_id = %s
            """, (ListID))
            ## Clear the Gui of Folders belonging to the List
            self.listTab.FolderTreeModel.clear()
            ## Clear the list name from the Gui
            TreeModel.remove(listIter)
            ListDeleteButton.set_sensitive(False)
            FileDeleteButton.set_sensitive(False)
            FileAddButton.set_sensitive(False)
            RefreshListButton.set_sensitive(False)
        else: 
            self.sdError.UserError('This list is active in a channel\n remove the list from use before deleting')

        listNum=self.dbc.dbFetchRow('''
        select count(list_id) from list_names''')
        if (listNum > 0):
            ButtonChannelAdd.set_sensitive(True)
        else:
            ButtonChannelAdd.set_sensitive(False)

        self.channelTab.InitializeNewListCombo(self.channelTab.NewComboModel)
        self.channelTab.InitializeNewListCombo(self.channelTab.EditComboModel)

                             
    def on_btnNewList_clicked(self, widget, userdata=None):
        NewDialog = self.builder.get_object('ListNewDialog')
        NewListName = self.builder.get_object('NewListName')
        FileFolder = self.builder.get_object('FileFolder')
        FileFolder.set_current_folder(os.path.expanduser('~'))
        NewDialog.show_all()
        NewListName.grab_focus()
                
    def on_btnFileLocationDelete_clicked(self, widget, userdata=None):
        ListSelection=self.listTab.ListTreeView.get_selection()
        (TreeModel, listIter) = ListSelection.get_selected()
        ListSelected=TreeModel.get_value(listIter,0)
        ListID=self.dbc.dbFetchRow("""
        select list_id from list_names where list_name = %s
        """ , (ListSelected))
        try:  ## only try to remove if something is selected
            FolderSelection=self.listTab.FolderTreeView.get_selection()
            (TreeModel, folderIter) = FolderSelection.get_selected()
            FolderSelected=TreeModel.get_value(folderIter,0)
            FolderID=self.dbc.dbFetchRow("""
            select list_dir_id from list_dirs where dir_name = %s
            """, (FolderSelected))
            ## Remove from FolderTree
            TreeModel.remove(folderIter)
            ## Remove List Association
            self.dbc.dbDeleteRow('''
            delete from list_name_dir where list_dir_id = %s
            and list_id = %s
            ''', (FolderID, ListID))
            ## Check to see if any other lists are using this folder
            CountRemaining=self.dbc.dbFetchRow("""
            select count(*) from list_name_dir where list_dir_id = %s
            """, (FolderID))
            if (int(CountRemaining) == 0):
                ## Remove the folder from the DB
                self.dbc.dbDeleteRow("""
                delete from list_dirs where list_dir_id = %s
                """, (FolderID))
            ## Check the count of foldersremaining for list
            FoldersLeft=self.dbc.dbFetchRow("""
            select count(list_dir_id) from list_name_dir where list_id = %s
            """, (ListID))
            if (FoldersLeft):
                delDirBtn=self.builder.get_object('btnFileLocationDelete')
                if (int(FoldersLeft) == 1):
                    delDirBtn.set_sensitive(False)
        except TypeError:
            pass
    
    def on_btnFileLocationAdd_clicked(self, widget, userdata=None):
        FileDialog = self.builder.get_object('AddDirectoryDialog')
        FileDialog.set_current_folder(os.path.expanduser('~'))
        FileDialog.show_all()

    ## New List Dialog Callbacks
    def on_DialogOK_clicked(self, widget, userdata=None):
        NewListDialog=self.builder.get_object('ListNewDialog')
        ListName=self.builder.get_object('NewListName')
        FolderName=self.builder.get_object('FileFolder')
        NewListDialog.hide()
        if(len(ListName.get_text().strip()) > 0):
            NameAdded=self.dbc.PushListDB(ListName.get_text().strip())
            if (NameAdded):
                listIter=self.listTab.PushListGUI(ListName.get_text().strip())
                self.listTab.ListTreeSelection.select_iter(listIter)
                listID=self.dbc.dbLastInsertID("list_names", "list_id")
                folderIter=self.listTab.PushFolderGUI(FolderName.get_filename(),0)
                self.channelTab.PushListCombo(self.channelTab.NewComboModel,ListName.get_text())
                self.channelTab.PushListCombo(self.channelTab.EditComboModel,ListName.get_text())
                if (folderIter):
                    self.dbc.PushFolderDB(FolderName.get_filename())
                    folderID=self.dbc.dbLastInsertID("list_dirs", "list_dir_id")
                    ListName.set_text('')
                    mergeID=self.dbc.dbInsertRow("""
                        insert into list_name_dir (list_id, list_dir_id)
                        values (%s, %s)""", (listID, folderID))
                    self.listTab.FolderTreeSelection.select_iter(folderIter)
                ListName.set_text('')
            else:
                ListName.set_text('')
        ButtonChannelAdd=self.builder.get_object('btnAddChannel')
        listNum=self.dbc.dbFetchRow('''
        select count(list_id) from list_names''')
        if (listNum > 0):
            ButtonChannelAdd.set_sensitive(True)
        else:
            ButtonChannelAdd.set_sensitive(False)


    def on_DialogCancel_clicked(self, widget, userdata=None):
        ListName=self.builder.get_object('NewListName')
        ListName.set_text('')
        NewDialog = self.builder.get_object('ListNewDialog')
        NewDialog.hide()
        
    ## Add Directory Dialog Callbacks
    def on_FileCancelButton_clicked(self, widget, userdata=None):
        AddDirDialog=self.builder.get_object('AddDirectoryDialog')
        AddDirDialog.hide()
        
    def on_FileOpenButton_clicked(self, widget, userdata=None):
        ListSelection=self.listTab.ListTreeView.get_selection()
        (TreeModel, listIter) = ListSelection.get_selected()
        ListSelectValue=TreeModel.get_value(listIter,0)
        listID=self.dbc.dbFetchRow('''
        select list_id from list_names where list_name = %s''',
                                         (ListSelectValue))
        AddDirDialog=self.builder.get_object('AddDirectoryDialog')
        folderAddDB=self.dbc.PushFolderDB(AddDirDialog.get_filename())
        folderIter=self.listTab.PushFolderGUI(AddDirDialog.get_filename(),0)
        AddDirDialog.hide()
        if (folderIter):
            folderID=self.dbc.dbFetchRow('''
            select list_dir_id from list_dirs where dir_name = %s''',
                                    (AddDirDialog.get_filename()))
            mergeID=self.dbc.dbInsertRow("""
                insert into list_name_dir (list_id, list_dir_id)
                values (%s, %s)""", (listID, folderID))

## Channel Tab Callbacks
    def BuildListBtn_clicked_cb(self, widget, userdata=None):
        (dModel,dIter)=self.channelTab.ChannelDetailSelection.get_selected()
        NickName=dModel.get_value(dIter,0)
        ListName=dModel.get_value(dIter,1)
        Progress=self.builder.get_object('BuildListProgressWindow')
        Progress.show_all()
        GenThread = Thread(target=BuildList, \
                    args=(self.builder, self.dbc, \
                    NickName, ListName, self.ProgressEvent))
        GenThread.start()

   
    def btnAddChannel_clicked_cb(self, widget, userdata=None):
        NewChannelWin=self.builder.get_object('NewChannelWindow')
        NewChannelWin.show_all()

    def btnDelChannel_clicked_cb(self, widget, userdata=None):
        (tModel,tIter)=self.channelTab.ChannelTreeSelection.get_selected()
        NetworkName=tModel.get_value(tIter,0)
        ChannelName=tModel.get_value(tIter,1)
        NetworkID=self.dbc.dbFetchRow('''
        select network_id from networks where network_name = %s
        ''', (NetworkName))
        Nicks=self.dbc.dbFetchAll('''
        select distinct nick_id from channels where network_id = %s
        ''', (NetworkID))
        NetworkCount=self.dbc.dbFetchRow('''
        select count(network_id) as NetworkRemain
        from channels where network_id = %s
        ''', (NetworkID))
        if (NetworkCount <= 0):
            self.dbc.dbDeleteRow('''
            delete from networks where network_id = %s
            ''', (NetworkID))
        for Nick in Nicks:
            NickCount=self.dbc.dbFetchRow('''
            select distinct count(nick_id) as NickRemain
            from channels where nick_id = %s
            ''', (Nick["nick_id"]))
            if (NickCount <= 0):
                self.dbc.dbDeleteRow('''
                delete from serving_nicks where nick_id = %s
                ''', (NickID))
        self.dbc.dbDeleteRow('''
        delete from channels where network_id = %s
        ''', (NetworkID))
        self.channelTab.ChannelDetailModel.clear()
        self.channelTab.InitializeChannelTree()

   
    def btnEditChannel_clicked_cb(self, widget, userdata=None):
        EditChannelWin=self.builder.get_object('EditChannelWindow')
        (tModel,tIter)=self.channelTab.ChannelTreeSelection.get_selected()
        (dModel,dIter)=self.channelTab.ChannelDetailSelection.get_selected()
        NickName=dModel.get_value(dIter,0)
        ListName=dModel.get_value(dIter,1)
        Freq=dModel.get_value(dIter,2)
        AdCheck=dModel.get_value(dIter,3)
        RandCheck=dModel.get_value(dIter,4)
        NetworkName=tModel.get_value(tIter,0)
        ChannelName=tModel.get_value(tIter,1)
        Found=self.channelTab.EditComboModel.get_iter_first()
        while (Found != None):
            if (ListName == self.channelTab.EditComboModel.get_value(Found,0)):
                self.builder.get_object('EditListCombo').set_active_iter(Found)
                break
            else:
                Found = self.channelTab.EditComboModel.iter_next(Found)
        
        ChannelID=self.dbc.dbFetchRow('''
        select C.channel_id from
        channels C, list_names L, serving_nicks S, networks N
        where C.list_id = L.list_id
        and C.nick_id = S.nick_id
        and C.network_id = N.network_id
        and N.network_name = %s
        and L.list_name = %s
        and S.nick_name = %s
        and C.channel_name = %s
        ''', (NetworkName, ListName, NickName, ChannelName))
        self.builder.get_object('EditChannelID').set_text(str(ChannelID))
        self.builder.get_object('EditNetworkLabelValue').set_text(NetworkName)
        self.builder.get_object('EditChannelLabelValue').set_text(ChannelName)
        self.builder.get_object('EditNickEntry').set_text(NickName)
        self.builder.get_object('EditAdFreqSpin').set_value(int(Freq))
        RandTextBuf=self.builder.get_object('EditTextBeforeRandom').get_buffer()
        AdTextBuf=self.builder.get_object('EditTextBeforeAd').get_buffer()
        if (AdCheck == 'True'):
            AdCheck=1
            self.builder.get_object('EditBeforeAdCheck').set_active(True)
            self.builder.get_object('EditTextBeforeAd').set_sensitive(True)
            AdText=self.dbc.dbFetchRow('''
            select text_before_ad from channels where channel_id = %s
            ''', (ChannelID))
            AdTextBuf.set_text(AdText)
        else:
            AdCheck=0
            self.builder.get_object('EditBeforeAdCheck').set_active(False)
            self.builder.get_object('EditTextBeforeAd').set_sensitive(False)
            AdTextBuf.set_text('')
        if (RandCheck == 'True'):
            RandCheck=1
            self.builder.get_object('EditBeforeRandomCheck').set_active(True)
            self.builder.get_object('EditTextBeforeRandom').set_sensitive(True)
            RandText=self.dbc.dbFetchRow('''
            select text_before_rand from channels where channel_id = %s
            ''', (ChannelID))
            RandTextBuf.set_text(RandText)
        else:
            RandCheck=0
            self.builder.get_object('EditBeforeRandomCheck').set_active(False)
            self.builder.get_object('EditTextBeforeRandom').set_sensitive(False)
            RandTextBuf.set_text('')
        EditChannelWin.show_all()

    def ChannelDetailDelBtn_clicked_cb(self, widget, userdata=None):
        (tModel,tIter)=self.channelTab.ChannelTreeSelection.get_selected()
        (dModel,dIter)=self.channelTab.ChannelDetailSelection.get_selected()
        NetworkName=tModel.get_value(tIter,0)
        ChannelName=tModel.get_value(tIter,1)
        NickName=dModel.get_value(dIter,0)
        ListName=dModel.get_value(dIter,1)
        ChannelID=self.dbc.dbFetchRow('''
        select C.channel_id from
        channels C, list_names L, serving_nicks S, networks N
        where C.list_id = L.list_id
        and C.nick_id = S.nick_id
        and C.network_id = N.network_id
        and N.network_name = %s
        and L.list_name = %s
        and S.nick_name = %s
        and C.channel_name = %s
        ''', (NetworkName, ListName, NickName, ChannelName))
        self.dbc.dbDeleteRow('''
        delete from channels where channel_id = %s
        ''', (ChannelID))
        self.channelTab.ChannelDetailModel.clear()
        self.channelTab.PushChannelDetails(NetworkName, ChannelName)

    ## Edit Channel Window Callbacks   
    def EditChannelOKBtn_clicked_cb(self, widget, userdata=None):
        ok=True
        Network=self.builder.get_object('EditNetworkLabelValue').get_text()
        Channel=self.builder.get_object('EditChannelLabelValue').get_text()
        EditChannelWin=self.builder.get_object('EditChannelWindow')
        ChannelID=self.builder.get_object('EditChannelID').get_text()
        Nick=self.builder.get_object('EditNickEntry').get_text().strip()
        Freq=self.builder.get_object('EditAdFreqSpin').get_value()
        ListSelection=self.channelTab.EditComboBox.get_active_iter()
        List=self.channelTab.EditComboModel.get_value(ListSelection,0)
                                           
        if (self.builder.get_object('EditBeforeAdCheck').get_active()):
            AdCheck=1
            AdTextBuf=self.builder.get_object('EditTextBeforeAd').get_buffer()
            AdIterStart=AdTextBuf.get_start_iter()
            AdIterEnd=AdTextBuf.get_end_iter()
            AdText=AdTextBuf.get_text(AdIterStart, AdIterEnd, True)
        else:
            AdCheck=0
            AdText=''
        
        if (self.builder.get_object('EditBeforeRandomCheck').get_active()):
            RandCheck=1
            RandTextBuf=self.builder.get_object('EditTextBeforeRandom').get_buffer()
            RandIterStart=RandTextBuf.get_start_iter()
            RandIterEnd=RandTextBuf.get_end_iter()
            RandText=RandTextBuf.get_text(RandIterStart, RandIterEnd, True)
        else:
            RandCheck=0
            RandText=''

        if (len(Nick) <= 0):
            self.sdError.UserError('Serving Nick is Required')
            ok=False

        if (ok):
            self.dbc.PushNickDB(Nick)
            NickID=self.dbc.dbFetchRow('''
            select nick_id from serving_nicks where nick_name = %s
            ''', (Nick))
            ListID=self.dbc.dbFetchRow('''
            select list_id from list_names where list_name = %s
            ''', (List))
            try:
                self.dbc.dbUpdateRow('''
                update channels set
                nick_id = %s,
                list_id = %s,
                ad_frequency = %s,
                text_before_ad_bool = %s,
                text_before_rand_bool = %s,
                text_before_ad = %s,
                text_before_rand = %s
                where channel_id = %s
                ''', (NickID, ListID, Freq, AdCheck, RandCheck, AdText, RandText, ChannelID))
                EditChannelWin.hide()
                self.channelTab.ChannelDetailModel.clear()
                self.channelTab.PushChannelDetails(Network, Channel)
                self.builder.get_object('btnEditChannel').set_sensitive(False)
                self.builder.get_object('ChannelDetailDelBtn').set_sensitive(False)
                self.builder.get_object('BuildListBtn').set_sensitive(False)
            except MySQLdb.IntegrityError, e:
                self.sdError.UserError('Channel Already Exists')

    def EditChannelCancelBtn_clicked_cb(self, widget, userdata=None):
        EditChannelWin=self.builder.get_object('EditChannelWindow')
        EditChannelWin.hide()

    def EditBeforeAdCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.builder.get_object('EditTextBeforeAd').set_sensitive(True)
        else:
            self.builder.get_object('EditTextBeforeAd').set_sensitive(False)

    def EditBeforeRandomCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.builder.get_object('EditTextBeforeRandom').set_sensitive(True)
        else:
            self.builder.get_object('EditTextBeforeRandom').set_sensitive(False)

    def BuildListProgressWindow_destroy_cb(self, widget, userdata=None):
        Progress=self.builder.get_object('BuildListProgressWindow')
        Progress.hide()

    def BuildListProgressBtn_clicked_cb(self, widget, userdata=None):
        self.ProgressEvent.set()
        Progress=self.builder.get_object('BuildListProgressWindow')
        Progress.hide()

    ## New Channel Window Callbacks
    def NewChannelOKBtn_clicked_cb(self, widget, userdata=None):
        ok=True
        NewChannelWin=self.builder.get_object('NewChannelWindow')
        Network=self.builder.get_object('TextNetworkEntry').get_text().strip()
        Channel=self.builder.get_object('TextChannelEntry').get_text().strip()
        Nick=self.builder.get_object('NewNickEntry').get_text().strip()
        Freq=self.builder.get_object('NewAdFreqSpin').get_value()
        if (self.builder.get_object('NewBeforeAdCheck').get_active()):
            AdCheck=1
            AdTextBuf=self.builder.get_object('NewTextBeforeAd').get_buffer()
            AdIterStart=AdTextBuf.get_start_iter()
            AdIterEnd=AdTextBuf.get_end_iter()
            AdText=AdTextBuf.get_text(AdIterStart, AdIterEnd, True)
        else:
            AdCheck=0
            AdText=''
        
        if (self.builder.get_object('NewBeforeRandomCheck').get_active()):
            RandCheck=1
            RandTextBuf=self.builder.get_object('NewTextBeforeRandom').get_buffer()
            RandIterStart=RandTextBuf.get_start_iter()
            RandIterEnd=RandTextBuf.get_end_iter()
            RandText=RandTextBuf.get_text(RandIterStart, RandIterEnd, True)
        else:
            RandCheck=0
            RandText=''
        
        Selection=self.channelTab.NewComboBox.get_active_iter()
        try:
            List=self.channelTab.NewComboModel.get_value(Selection,0)
        except TypeError, e:
            self.sdError.UserError('You must Select a List to serve')
            ok=False
            
        if (len(Network) <= 0):
            self.sdError.UserError('Network is Required')
            ok=False
        elif (len(Channel) <= 0):
            self.sdError.UserError('Channel is Required')
            ok=False
        elif (len(Nick) <= 0):
            self.sdError.UserError('Serving Nick is Required')
            ok=False

        if (ok):
            self.dbc.PushNetworkDB(Network)
            self.dbc.PushNickDB(Nick)
            if (self.dbc.PushChannelDB(Network,Channel,Nick,List,Freq,\
                                       AdCheck,RandCheck,AdText,RandText)):
                NewChannelWin.hide()
                self.channelTab.InitializeChannelTree()
                self.channelTab.ChannelDetailModel.clear()
                self.builder.get_object('TextNetworkEntry').set_text('')
                self.builder.get_object('TextChannelEntry').set_text('')
                self.builder.get_object('NewNickEntry').set_text('')
                self.builder.get_object('NewAdFreqSpin').set_value(300)
                self.builder.get_object('NewBeforeAdCheck').set_active(False)
                self.builder.get_object('NewBeforeRandomCheck').set_active(False)
                try:
                    AdTextBuf.delete(AdIterStart, AdIterEnd)
                    RandTextBuf.delete(RandIterStart, RandIterEnd)
                except UnboundLocalError, e:
                    pass  ##only delete them if they exist
                self.channelTab.NewComboBox.set_active(-1)

    def NewChannelCancelBtn_clicked_cb(self, widget, userdata=None):
        NewChannelWin=self.builder.get_object('NewChannelWindow')
        NewChannelWin.hide()
        self.builder.get_object('TextNetworkEntry').set_text('')
        self.builder.get_object('TextChannelEntry').set_text('')
        self.builder.get_object('NewNickEntry').set_text('')
        self.builder.get_object('NewAdFreqSpin').set_value(300)
        self.builder.get_object('NewBeforeAdCheck').set_active(False)
        self.builder.get_object('NewBeforeRandomCheck').set_active(False)
        RandTextBuf=self.builder.get_object('NewTextBeforeRandom').get_buffer()
        RandIterStart=RandTextBuf.get_start_iter()
        RandIterEnd=RandTextBuf.get_end_iter()
        AdTextBuf=self.builder.get_object('NewTextBeforeAd').get_buffer()
        AdIterStart=AdTextBuf.get_start_iter()
        AdIterEnd=AdTextBuf.get_end_iter()
        try:
            AdTextBuf.delete(AdIterStart, AdIterEnd)
            RandTextBuf.delete(RandIterStart, RandIterEnd)
        except UnboundLocalError, e:
            pass  ##only delete them if they exist
        self.channelTab.NewComboBox.set_active(-1)
        
    def BeforeAdCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.builder.get_object('NewTextBeforeAd').set_sensitive(True)
        else:
            self.builder.get_object('NewTextBeforeAd').set_sensitive(False)


    def BeforeRandomCheck_toggled_cb(self, widget, userdata=None):
        chkbtn = self.builder.get_object(widget.name)
        if (chkbtn.get_active()):
            self.builder.get_object('NewTextBeforeRandom').set_sensitive(True)
        else:
            self.builder.get_object('NewTextBeforeRandom').set_sensitive(False)

## Statistics Tab
    def btnResetStats_clicked_cb(self, widget, userdata=None):
        self.statsTab.ResetStats()
        self.statsTab.UpdateStats()

    def btnViewQueue_clicked_cb(self, widget, userdata=None):
        columnNames = [('NickColumn','Nick','150', True),
                       ('QueueColumn','Queue','75', False),
                       ('NetworkColumn','Network','150', True),
                       ('ChannelColumn','Channel','150', True)]
        TreeModel=gtk.ListStore(gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING)
        (QueueTree, QueueModel, QueueSelection) = \
                self.statsTab.BuildStatsView(columnNames, TreeModel)
        Queues=self.dbc.dbFetchAll('''
        select 
                Q.queue_number as QueueNum, 
                S.nick as NickName, 
                C.channel_name as ChannelName, 
                N.network_name as NetworkName
        from 
                queues Q, nick_served S,
                channels C, networks N
        where
                Q.nick_id = S.nick_id
            and Q.channel_id = C.channel_id
            and Q.network_id = N.network_id''')

        try:
            for Queue in Queues:
                Iter=QueueModel.insert_before(None, None)
                QueueModel.set_value(Iter,0,Queue["NickName"])
                QueueModel.set_value(Iter,1,Queue["QueueNum"])
                QueueModel.set_value(Iter,2,Queue["ChannelName"])
                QueueModel.set_value(Iter,3,Queue["NetworkName"])
        except TypeError, e:
            pass #query returned no rows

    def btnViewBans_clicked_cb(self, widget, userdata=None):
        columnNames = [('NickColumn','Nick','150', True),
                       ('ReasonColumn','Reason Code','100', False),
                       ('NetworkColumn','Network','150', True),
                       ('ChannelColumn','Channel','125', True)]
        TreeModel=gtk.ListStore(gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING)
        (BanTree, BanModel, BanSelection) = \
                self.statsTab.BuildStatsView(columnNames, TreeModel)
        Bans = self.dbc.dbFetchAll('''
        select 
                B.ban_code as Code,
                S.nick as NickName,
                N.network_name as NetworkName,
                C.channel_name as ChannelName
        from
                nick_bans B, nick_served S,
                networks N, channels C
        where
                B.nick_id = S.nick_id
            and B.network_id = N.network_id
            and B.channel_id = C.channel_id''')
        try:
            for Ban in Bans:
                Iter=BanModel.insert_before(None, None)
                BanModel.set_value(Iter,0,Ban["NickName"])
                BanModel.set_value(Iter,1,Ban["Code"])
                BanModel.set_value(Iter,2,Ban["ChannelName"])
                BanModel.set_value(Iter,3,Ban["NetworkName"])
        except:
            pass #query returned no rows
                
    def btnDetailStats_clicked_cb(self, widget, userdata=None):
        columnNames = [('NickColumn','Nick','150', True),
                       ('RequestColumn','Files Requested','125', False),
                       ('SentColumn','Files Received','125', False),
                       ('Size Column','MB Served','100', False)]
        TreeModel=gtk.ListStore(gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING, \
                                gobject.TYPE_STRING)
        (NickDetailTree, NickDetailModel, NickDetailSelection) = \
                self.statsTab.BuildStatsView(columnNames, TreeModel)

        NickStats = self.dbc.dbFetchAll('''
        select 
                S.nick as NickName,
                N.number_requested as FilesReq,
                N.number_received as FilesRec,
                N.size_received as SizeMB
        from
                nick_stats N, nick_served S
        where
                N.nick_id = S.nick_id''')

        try:
            for NickStat in NickStats:
                Iter=NickDetailModel.insert_before(None, None)
                NickDetailModel.set_value(Iter,0,NickStat["NickName"])
                NickDetailModel.set_value(Iter,1,NickStat["FilesReq"])
                NickDetailModel.set_value(Iter,2,NickStat["FilesRec"])
                NickDetailModel.set_value(Iter,3,NickStat["SizeMB"])
        except TypeError, e:
            pass # Query returned No rows


    def btnUpdateStats_clicked_cb(self, widget, userdata=None):
        self.statsTab.UpdateStats()
    
## Error Dialog Callbacks
    def on_ErrorDialog_response(self, widget, userdata=None):
        ErrorDlg = self.builder.get_object('ErrorDialog')
        ErrorDlg.hide()

    def on_FatalErrorDialog_response(self, widget, userdata=None):
        FatalErrorDlg = self.builder.get_object('FatalErrorDialog')
        sys.exit(255)

## Initialization    
    def __init__(self, builder, dbc, GuiOptions, \
            LoggingList, listTab, channelTab, statsTab, PriorityList, sdError):
        Thread.__init__(self)
        self.builder=builder
        self.dbc=dbc
        self.GuiOptions=GuiOptions
        self.LoggingList=LoggingList
        self.listTab=listTab
        self.channelTab=channelTab
        self.statsTab=statsTab
        self.PriorityList=PriorityList
        self.sdError=sdError
        self.ProgressEvent=Event()

