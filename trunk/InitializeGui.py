import gtk
from threading import Thread

class InitializeGui(Thread):
    """
    Class to initialize the Default/Saved Variables for the GUI
    """

    def InitMainTab(self):
        """ 
        Initialize the Main Tab of the GUI
        """
        self.GuiOptions['ServingDirectory'] = self.dbc.dbFetchRow('''
        select serving_directory from options limit 1
        ''')
        dbServingDirectory = self.builder.get_object('ServingDirectory')
        try:
            dbServingDirectory.set_current_folder(self.GuiOptions['ServingDirectory'])
        except:
            pass  # use default if not set
        self.GuiOptions['ServerPriority'] = self.dbc.dbFetchRow('''
                select server_priority from priority limit 1
                ''')
        for item in self.PriorityList.items():
            if (item[1] == self.GuiOptions['ServerPriority']):
                radioPri=self.builder.get_object(item[0])
                radioPri.set_active(True)
        self.GuiOptions['ExtentionEntry'] = self.dbc.dbFetchRow('''
                select priority_extentions from priority limit 1
                ''')
        dbExtentionEntry = self.builder.get_object('ExtentionEntry')
        dbExtentionEntry.set_text(self.GuiOptions['ExtentionEntry'])
        return 

    def InitOptionsTab(self):
        """
        Initialize the Options Tab for the GUI
        """

        self.GuiOptions['SendSlots'] = self.dbc.dbFetchRow('''
        select send_slots_num from options limit 1
        ''')
        dbSendSlots=self.builder.get_object('SendSlots')
        dbSendSlots.set_value(self.GuiOptions['SendSlots'])

        self.GuiOptions['DynamicSlots'] = self.dbc.dbFetchRow('''
        select dynamic_slots_num from options limit 1
        ''')
        dbDynamicSlots=self.builder.get_object('DynamicSlots')
        dbDynamicSlots.set_value(self.GuiOptions['DynamicSlots'])

        self.GuiOptions['FilesInQueue'] = self.dbc.dbFetchRow('''
        select queue_nick_num from options limit 1
        ''')
        dbFilesInQueue=self.builder.get_object('FilesInQueue')
        dbFilesInQueue.set_value(self.GuiOptions['FilesInQueue'])

        self.GuiOptions['QueueFull'] = self.dbc.dbFetchRow('''
        select queue_full_num from options limit 1
        ''')
        dbQueueFull=self.builder.get_object('QueueFull')
        dbQueueFull.set_value(self.GuiOptions['QueueFull'])

        self.GuiOptions['SmallLowCps'] = self.dbc.dbFetchRow('''
        select sm_file_low_cps from options limit 1
        ''')
        dbSmallLowCps=self.builder.get_object('SmallLowCps')
        dbSmallLowCps.set_value(self.GuiOptions['SmallLowCps'])

        self.GuiOptions['LargeLowCps'] = self.dbc.dbFetchRow('''
        select lg_file_low_cps from options limit 1
        ''')
        dbLargeLowCps=self.builder.get_object('LargeLowCps')
        dbLargeLowCps.set_value(self.GuiOptions['LargeLowCps'])

        self.GuiOptions['LargeFileSize'] = self.dbc.dbFetchRow('''
        select lg_file_size_mb from options limit 1
        ''')
        dbLargeFileSize=self.builder.get_object('LargeFileSize')
        dbLargeFileSize.set_value(self.GuiOptions['LargeFileSize'])

        self.GuiOptions['QueueListCheck'] = self.dbc.dbFetchRow('''
        select queue_list_bool from options limit 1
        ''')
        dbQueueListCheck=self.builder.get_object('QueueListCheck')
        dbMaxListQueue=self.builder.get_object('MaxListQueue')
        if (self.GuiOptions['QueueListCheck'] != 0):
            dbQueueListCheck.set_active(True)
            dbMaxListQueue.set_sensitive(True)
        else:
            dbQueueListCheck.set_active(False)
            dbMaxListQueue.set_sensitive(False)

        self.GuiOptions['MaxListQueue'] = self.dbc.dbFetchRow('''
        select max_list_queue from options limit 1
        ''')
        dbMaxListQueue.set_value(self.GuiOptions['MaxListQueue'])

        self.GuiOptions['SendCtcpCheck'] = self.dbc.dbFetchRow('''
        select send_ctcp_bool from options limit 1
        ''')
        dbSendCtcpCheck=self.builder.get_object('SendCtcpCheck')
        dbSendCtcpFreq=self.builder.get_object('SendCtcpFreq')
        if (self.GuiOptions['SendCtcpCheck'] != 0):
            dbSendCtcpCheck.set_active(True)
            dbSendCtcpFreq.set_sensitive(True)
        else:
            dbSendCtcpCheck.set_active(False)
            dbSendCtcpFreq.set_sensitive(False)

        self.GuiOptions['SendCtcpFreq'] = self.dbc.dbFetchRow('''
        select ctcp_send_freq from options limit 1
        ''')
        dbSendCtcpFreq.set_value(self.GuiOptions['SendCtcpFreq'])

        self.GuiOptions['RandomPlayCheck'] = self.dbc.dbFetchRow('''
        select rndm_play_bool from options limit 1
        ''')
        dbRandomNewTextCheck=self.builder.get_object('NewBeforeRandomCheck')
        dbRandomEditTextCheck=self.builder.get_object('EditBeforeRandomCheck')
        dbRandomPlayCheck=self.builder.get_object('RandomPlayCheck')
        dbRandomPlayFreq=self.builder.get_object('RandomPlayFreq')
        if (self.GuiOptions['RandomPlayCheck'] != 0):
            dbRandomPlayCheck.set_active(True)
            dbRandomPlayFreq.set_sensitive(True)
            dbRandomNewTextCheck.set_sensitive(True)
            dbRandomEditTextCheck.set_sensitive(True)
        else:
            dbRandomPlayCheck.set_active(False)
            dbRandomPlayFreq.set_sensitive(False)
            dbRandomNewTextCheck.set_sensitive(False)
            dbRandomEditTextCheck.set_sensitive(False)

        dbZipListCheck=self.builder.get_object('ZipListCheck')
        self.GuiOptions['ZipListCheck'] = self.dbc.dbFetchRow('''
        select zip_lists_bool from options limit 1
        ''')
        if (self.GuiOptions['ZipListCheck'] != 0):
            dbZipListCheck.set_active(True)
        else:
            dbZipListCheck.set_active(False)


        self.GuiOptions['RandomPlayFreq'] = self.dbc.dbFetchRow('''
        select rndm_play_freq from options limit 1
        ''')
        dbRandomPlayFreq.set_value(self.GuiOptions['RandomPlayFreq'])

        self.GuiOptions['EnableFindCheck'] = self.dbc.dbFetchRow('''
        select enable_find_bool from options limit 1
        ''')
        dbEnableFindCheck=self.builder.get_object('EnableFindCheck')
        dbMaxFindNum=self.builder.get_object('MaxFindNum')
        if (self.GuiOptions['EnableFindCheck'] != 0):
            dbEnableFindCheck.set_active(True)
            dbMaxFindNum.set_sensitive(True)
        else:
            dbEnableFindCheck.set_active(False)
            dbMaxFindNum.set_sensitive(False)

        self.GuiOptions['MaxFindNum'] = self.dbc.dbFetchRow('''
        select max_find_results from options limit 1
        ''')
        dbMaxFindNum.set_value(self.GuiOptions['MaxFindNum'])

        self.GuiOptions['radioLogging'] = self.dbc.dbFetchRow('''
        select log_option from options limit 1
        ''')
        for item in self.LoggingList.items():
            if (item[1] == self.GuiOptions['radioLogging']):
                radioLog=self.builder.get_object(item[0])
                radioLog.set_active(True)

    def __init__(self,builder,dbc,GuiOptions, LoggingList, PriorityList):
        Thread.__init__(self)

        self.builder=builder
        self.dbc=dbc
        self.GuiOptions=GuiOptions
        self.LoggingList=LoggingList
        self.PriorityList=PriorityList

        gtk.gdk.threads_enter()
        self.InitMainTab()
        gtk.gdk.threads_leave()

        gtk.gdk.threads_enter()
        self.InitOptionsTab()
        gtk.gdk.threads_leave()

