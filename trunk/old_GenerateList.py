import gtk
import os, time, sys
import stat
import mutagen.id3, mutagen.mp3
from threading import Thread
    
class GenerateList(Thread):
    '''
    Receives the "list name" from the user's selection.
    Walks each directory "recursively if requierd"
    reading the ID3 Tags from each MP3 and loading that information
    in the Database.
    '''

    def _is_vbr(self, file):
        '''
        Logic for the "for i in..." loop was taken from
        the mutagen version 1.15 source code in "mp3.py" 
        The mutagen module as of version 1.15
        does not supply a method to directly access
        this flag. We will assume if the file has a
        Xing or VBRI header it has a Variable Bit Rate
        '''
        try:
            size = os.path.getsize(file)
        except (IOError, OSError, AttributeError):
            return 0
        try:
            fileobj = open(file, 'rb+')
        except IOError:
            return 0
        # Break the search into 30 60 and 90% of size
        # to hopefully make it more efficient
        for i in [0, 0.3*size, 0.6*size, 0.9*size]:
            fileobj.seek(i, 0)
            data = fileobj.read(32768)
            try:
                xing = data[:-4].index("Xing")
                fileobj.close()
                return 1
            except ValueError:
                try:
                    vbri = data[:-24].index("VBRI")
                    fileobj.close()
                    return 1
                except ValueError: 
                    pass
                else:
                    fileobj.close()
                    return 1
            else:
                fileobj.close()
                return 1
        fileobj.close()
        return 0
    
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

    def PushGenre(self,genrename):
        genreID=self.dbc.dbFetchRow('''
        select genre_id from genre
        where genre_name = %s limit 1
        ''', (genrename))
        if (genreID):
            return genreID
        else:
            NextID=self.dbc.dbFetchRow('''
            select max(genre_id)+1 from genre
            ''')
            self.dbc.dbInsertRow('''
            insert into genre (genre_id,genre_name)
            values(%s,%s)
            ''', (NextID, genrename))
            return NextID

    def PushAlbum(self,albumname):
        albumID=self.dbc.dbFetchRow('''
        select album_id from album
        where album_name = %s limit 1
        ''', (albumname))
        if (albumID):
            return albumID
        else:
            self.dbc.dbInsertRow('''
            insert into album (album_name)
            values(%s)
            ''', (albumname))
            albumID=self.dbc.dbFetchRow('''
            select album_id from album
            where album_name = %s limit 1
            ''', (albumname))
            return albumID

    def PushArtist(self,artistname):
        artistID=self.dbc.dbFetchRow('''
        select artist_id from artist
        where artist_name = %s limit 1
        ''', (artistname))
        if (artistID):
            return artistID
        else:
            self.dbc.dbInsertRow('''
            insert into artist (artist_name)
            values(%s)
            ''', (artistname))
            artistID=self.dbc.dbFetchRow('''
            select artist_id from artist
            where artist_name = %s limit 1
            ''', (artistname))
            return artistID

    def PushAlbumArtist(self,artistname):
        artistID=self.dbc.dbFetchRow('''
        select album_artist_id from album_artist
        where album_artist_name = %s limit 1
        ''', (artistname))
        if (artistID):
            return artistID
        else:
            self.dbc.dbInsertRow('''
            insert into album_artist (album_artist_name)
            values(%s)
            ''', (artistname))
            artistID=self.dbc.dbFetchRow('''
            select album_artist_id from album_artist
            where album_artist_name = %s limit 1
            ''', (artistname))
            return artistID
                        
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
   
    def ReadTags(self, ListName):
        ProcessFileLabel=self.builder.get_object('ProcessFileLabel')
        ProcessDirLabel=self.builder.get_object('ProcessDirLabel')
        ProgressBar=self.builder.get_object('ProgressBar')
        ProgressButton=self.builder.get_object('ProgressButton')
        gtk.gdk.threads_enter()
        ProgressBar.set_text('')
        ProgressButton.set_label('gtk-cancel')
        gtk.gdk.threads_leave()
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
                    select song_id from song
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
                        try:
                            gtk.gdk.threads_enter()
                            try:
                                ProcessFileLabel.set_text(u'File: %s' %(child))
                            except UnicodeDecodeError,e:
                                pass
                            ProgressBar.pulse()
                            time.sleep(0.01)
                            gtk.gdk.threads_leave()
                            try:
                                mp3=mutagen.mp3.MP3(filename)
                            except IOError:
                                continue
                            try:
                                id3=mutagen.id3.ID3(filename)
                            except:
                                continue
                            VBR=self._is_vbr(filename)                          
                            try:
                                AlbumArtist=self.PushAlbumArtist(id3["TPE2"])
                                if not isinstance(AlbumArtist,int):
                                    AlbumArtist='1'
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                AlbumArtist='1'
                            try:
                                Artist=self.PushArtist(id3["TPE1"])
                                if not isinstance(Artist,int):
                                    Artist='1'
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                Artist='1'
                            try:
                                Album=self.PushAlbum(id3["TALB"])
                                if not isinstance(Album,int):
                                    Album=1
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                Album='1'
                            try:
                                Genre=self.PushGenre(id3["TCON"])
                                if not isinstance(Genre,int):
                                    Genre='126'
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                Genre='126'
                            try:
                                Track=id3["TRCK"]
                                if not isinstance(Track,int):
                                    Track='1'
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                Track='1'
                            try:
                                Title=id3["TIT2"]
                            except (mutagen.id3.ID3NoHeaderError,KeyError),e:
                                Title=File
                            try:
                                Seconds=mp3.info.length
                                if not isinstance(Seconds,int):
                                    Seconds='0'
                            except (mutagen.mp3.HeaderNotFoundError,KeyError),e:
                                Seconds='0'
                            try:
                                BPM=mp3.info.bitrate
                                if not isinstance(BPM,int):
                                    BPM='0'
                            except (mutagen.mp3.HeaderNotFoundError,KeyError),e:
                                BPM='0'
                            try:
                                Sample=mp3.info.sample_rate
                                if not isinstance(Sample,int):
                                    Sample='0'
                            except (HeaderNotFoundError,KeyError),e:
                                Sample='0'
                            try:
                                Mode=mp3.info.mode
                                if not isinstance(Mode,int):
                                    Mode='0'
                            except (mutagen.mp3.HeaderNotFoundError,KeyError),e:
                                Mode='0'

                            song=self.dbc.dbInsertRow('''
                            insert into song
                            (song_name, file_name, track_num,
                            sample_rate, bitrate, vbr_bool,
                            duration_sec, file_mode_id,
                            genre_id, album_id, artist_id,
                            album_artist_id,directory_id) values
                            (%s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s)
                            ''', (Title, File, Track, Sample,
                                    BPM, VBR, Seconds, Mode,
                                    Genre, Album, Artist,
                                    AlbumArtist, DirID))

                        except (mutagen.id3.ID3NoHeaderError,\
                                mutagen.mp3.HeaderNotFoundError),e:
                            song=self.dbc.dbInsertRow('''
                            insert into song
                            (song_name, file_name, directory_id) values
                            (%s, %s, %s)''', (File, File, DirID))
                        
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
        self.ReadTags(self.ListName)
