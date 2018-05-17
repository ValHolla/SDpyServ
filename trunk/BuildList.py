
import gtk, gobject
import os, time, string, zipfile
from threading import Thread
        
class BuildList(Thread):
    
    def WriteList(self, NickName, ListName):
        ProgressDirLabel=self.builder.get_object('BuildListDirLbl')
        ProgressLabel=self.builder.get_object('BuildListLbl')
        ProgressBar=self.builder.get_object('BuildListProgress')
        ProgressButton=self.builder.get_object('BuildListProgressBtn')
        gtk.gdk.threads_enter()
        ProgressButton.set_label('gtk-cancel')
        gtk.gdk.threads_leave()
        ListDate=time.strftime("%Y%m%d")

        FileInfo = "Info Place Holder"
        filename=string.join((\
                string.join((NickName,ListName,ListDate),'-'),'txt'),'.')
        ServDir = self.dbc.dbFetchRow('''
                    select serving_directory from options''')
        if (not ServDir):
            ServDir = os.path.join(os.path.expanduser("~"),'.xchat2','SDpyServ')

        if (not os.path.exists(ServDir)):
            os.makedirs(ServDir,0755)
        elif (not os.path.isdir(ServDir)):
            os.unlink(ServDir)
            os.makedirs(ServDir,0755)

        filePath = os.path.join(ServDir,filename)
        gtk.gdk.threads_enter()
        ProgressDirLabel.set_text(u'Dir: %s' % (ServDir))
        ProgressLabel.set_text(u'List: %s' % (filename))
        gtk.gdk.threads_leave()

        ListCnt = float(self.dbc.dbFetchRow('''
                    select count(file_id) from list_contents'''))

        ListFiles = self.dbc.dbFetchAll('''
                    select F.directory_id as DirID, 
                    F.file_name as FileName
                    from file F, list_contents L
                    where F.file_id = L.file_id''')
        try:
            oFile = open(filePath,'w')
        except IOError, e:
            self.sdError.UserError('Can Not open file for writing')

        pctComplete=float(0.00)
        gtk.gdk.threads_enter()
        ProgressBar.set_fraction(pctComplete)
        gtk.gdk.threads_leave()
        if (ListCnt == 0):
            ListCnt += 1
        fileCnt = float(1)
        for file in ListFiles:
            if self.ProgressEvent.isSet():
                break
            oFile.write("!%s %d-%s ::INFO:: %s\n" % 
                    (NickName, file["DirID"], file["FileName"], FileInfo)) 
            gtk.gdk.threads_enter()
            ProgressBar.set_fraction(pctComplete)
            gtk.gdk.threads_leave()
            if (fileCnt < ListCnt):
                fileCnt += 1
                pctComplete = float(fileCnt / ListCnt)
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

        gtk.gdk.threads_enter()
        ProgressButton.set_label('gtk-ok')
        gtk.gdk.threads_leave()
        self.ProgressEvent.set()

    def __init__(self, builder, dbc, NickName, 
                    ListName, ProgressEvent):
        Thread.__init__(self)
        self.builder=builder
        self.dbc=dbc
        self.NickName=NickName
        self.ListName=ListName
        self.ProgressEvent=ProgressEvent
        self.ProgressEvent.clear()
        self.WriteList(self.NickName, self.ListName)

