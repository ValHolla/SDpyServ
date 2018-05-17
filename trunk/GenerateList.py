import gtk
import os, time, sys
import stat
from threading import Thread
    
class GenerateList(Thread):
    '''
    Receives the "list name" from the user's selection.
    Walks each directory "recursively if requierd"
    '''

    def _walktree(self, top=".", recurse=1):
        try:
            names = os.listdir(top)
        except (IOError, OSError, AttributeError):
            return
        if (recurse != 0):
            for name in names:
                try:
                    st = os.lstat(os.path.join(top, name))
                except (IOError, OSError, AttributeError):
                    continue
                if stat.S_ISDIR(st.st_mode):
                    for (newtop, children) in self._walktree \
                            (os.path.join(top, name), recurse):
                        yield newtop, children
        yield top, names

    def PushDirectory(self,dirname):
        dirID=self.dbc.dbFetchRow('''
        select directory_id from directory where directory_name = %s limit 1
        ''', (dirname))
        if (dirID):
            return dirID
        else:
            self.dbc.dbInsertRow('''
            insert into directory (directory_name) values (%s)
            ''', (dirname))
            dirID=self.dbc.dbFetchRow('''
            select directory_id from directory
            where directory_name = %s limit 1
            ''', (dirname))
            return dirID
   
    def AddToList(self, ListName):
        ProcessFileLabel=self.builder.get_object('ProcessFileLabel')
        ProcessDirLabel=self.builder.get_object('ProcessDirLabel')
        ProgressBar=self.builder.get_object('ProgressBar')
        ProgressButton=self.builder.get_object('ProgressButton')
        gtk.gdk.threads_enter()
        ProgressBar.set_text('')
        ProgressButton.set_label('gtk-cancel')
        gtk.gdk.threads_leave()
        LIST_ID=self.dbc.dbFetchRow('''
        select list_id from list_names
        where list_name = %s''', (ListName))

        DirList=self.dbc.dbFetchAll('''
        select LD.dir_name as "Name", LND.dir_recurse_bool as "Recurse"
        from list_dirs LD, list_name_dir LND, list_names LN
        where LD.list_dir_id = LND.list_dir_id
        and LN.list_id = LND.list_id
        and LN.list_name = %s
        ''', (ListName))
        for Dir in DirList:
            if self.ProgressEvent.isSet():
                break
            for (basepath, children) in self._walktree\
                    (Dir["Name"], Dir["Recurse"]):
                gtk.gdk.threads_enter()
                ProcessDirLabel.set_text(u'Folder: %s' % (basepath))
                gtk.gdk.threads_leave()

                if self.ProgressEvent.isSet():
                    break
                for child in children:
                    if self.ProgressEvent.isSet():
                        break

                    DirID=self.PushDirectory(basepath)
                    exist=self.dbc.dbFetchRow('''
                    select file_id from file
                    where directory_id = %s and file_name = %s
                    ''', (DirID, child))

                    if (exist):
                        continue

                    filename=os.path.join(basepath, child)
                    try:
                        st = os.lstat(filename)
                    except os.error:
                        continue

                    if stat.S_ISREG(st.st_mode):
                        File=child
                        gtk.gdk.threads_enter()
                        try:
                            ProcessFileLabel.set_text(u'File: %s' %(child))
                        except UnicodeDecodeError,e:
                            pass
                        ProgressBar.pulse()
                        time.sleep(0.01)
                        gtk.gdk.threads_leave()

                        file=self.dbc.dbInsertRow('''
                        insert into file
                        (file_name, directory_id) values
                        (%s, %s)''', (File, DirID))

                        FILE_ID=self.dbc.dbFetchRow('''
                        select file_id from file 
                        where file_name = %s
                        and directory_id = %s''', (File, DirID))

                        fc=self.dbc.dbInsertRow('''
                        insert into list_contents
                        (file_id, list_id) values
                        (%s, %s)''', (FILE_ID,LIST_ID))
                        
        gtk.gdk.threads_enter()
        ProcessFileLabel.set_text('File:')
        ProcessDirLabel.set_text('Folder:')
        ProgressBar.set_fraction(0.001)
        ProgressBar.set_text('Processing Complete')
        ProgressButton.set_label('gtk-ok')
        gtk.gdk.threads_leave()
        self.ProgressEvent.set()

    def __init__(self, builder, dbc, ListName, ProgressEvent):
        Thread.__init__(self)
        self.builder=builder
        self.dbc=dbc
        self.ListName=ListName
        self.ProgressEvent=ProgressEvent
        self.ProgressEvent.clear()
        self.AddToList(self.ListName)
