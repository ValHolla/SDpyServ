import MySQLdb
from threading import Thread

class DbCalls(Thread):

    def dbFetchRow(self, sql, data=None):
        cursor=self.dbc.cursor()
        cursor.execute(sql, data)
        result = cursor.fetchone()
        cursor.close()
        if (result):
            return result[0]
        else:
            return None

    def dbFetchAll(self, sql, data=None):
        cursor=self.dbc.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql, data)
        resultDict=cursor.fetchall()
        cursor.close()
        if (resultDict):
            return resultDict
        else:
            return None
    
    def dbInsertRow(self, sql, data=None):
        cursor=self.dbc.cursor()
        result=cursor.execute(sql, data)
        self.dbc.commit()
        cursor.close()
        return result

    def dbDeleteRow(self, sql, data=None):
        cursor=self.dbc.cursor()
        result=cursor.execute(sql, data)
        self.dbc.commit()
        cursor.close()
        return
    
    def dbUpdateRow(self, sql, data=None):
        cursor=self.dbc.cursor()
        result=cursor.execute(sql, data)
        self.dbc.commit()
        cursor.close
        return
    
    def dbRowCount(self, table, data=None):
        Sql="select count(*) from %s" %(table)
        return self.dbFetchRow(Sql)
    
    def dbLastInsertID(self, table,column, data=None):
        Sql="select max(%s) from %s" %(column, table)
        return self.dbFetchRow(Sql)
        
    def dbCloseConnection(self):
        self.dbc.close()

    def PushListDB(self,ListName):
        try:
            self.dbInsertRow("""
            insert into list_names (list_name) values (%s)
            """, (ListName))
        except MySQLdb.IntegrityError, e:
            self.sdError.UserError('A List by that name already Exists')
            return False
        return True

    def PushFolderDB(self,FolderName):
        EntryExists=self.dbFetchRow('''
        select list_dir_id from list_dirs where dir_name = %s
        ''', (FolderName))
        if (EntryExists):
            return
        else:        
            self.dbInsertRow("""
                insert into list_dirs (dir_name) values(%s)
                """, (FolderName))

    def PushNetworkDB(self, NetworkName):
        EntryExists=self.dbFetchRow('''
        select network_id from networks where network_name = %s
        ''', (NetworkName))
        if (EntryExists):
            return
        else:
            self.dbInsertRow("""
            insert into networks (network_name) values(%s)
            """, (NetworkName))

    def PushNickDB(self,Nick):
        EntryExists=self.dbFetchRow('''
        select nick_id from serving_nicks where nick_name = %s
        ''', (Nick))
        if (EntryExists):
            return
        else:
            self.dbInsertRow("""
            insert into serving_nicks (nick_name) values(%s)
            """, (Nick))

    def PushChannelDB(self,Network,Channel,Nick,\
                      List,Freq,AdChk,RndChk,AdText,\
                      RandText):
        NetworkID=self.dbFetchRow('''
        select network_id from networks where network_name = %s
        ''', (Network))
        NickID=self.dbFetchRow('''
        select nick_id from serving_nicks where nick_name = %s
        ''', (Nick))
        ListID=self.dbFetchRow('''
        select list_id from list_names where list_name = %s
        ''', (List))
        try:
            ChannelID=self.dbInsertRow("""
            insert into channels (channel_name, network_id,
                                  nick_id, list_id, ad_frequency,
                                  text_before_ad_bool,
                                  text_before_rand_bool,
                                  text_before_ad, text_before_rand)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (Channel, NetworkID, NickID, ListID, \
                  Freq, AdChk, RndChk, AdText, RandText))
            return True
        except MySQLdb.IntegrityError, e:
            self.sdError.UserError('Channel Already Exists with selected\nNetwork, Channel, Nick and List')
            return False
        
    def __init__(self, builder, config, sdError):
        Thread.__init__(self)

        self.config=config
        self.builder=builder
        self.sdError=sdError
        try:
            self.dbc = MySQLdb.connect(\
                host = config.get('Database','host'), \
                user = config.get('Database','user'), \
                passwd = config.get('Database','passwd'), \
                db = config.get('Database','db'))
        except:
            try:
                self.sdError.FatalError('Could Not connect to MySQL Database')
            except:
                print ('Could Not connect to MySQL Database')
