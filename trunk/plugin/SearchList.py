import string
import xchat

class SearchList():

    def FindFiles(self, FromNick, ServerContext, \
                     ChannelContext, SearchStr):
        self.Logger.PrintDebug("FromNick, %s" % (FromNick))
        self.Logger.PrintDebug("ServerContext, %s" % (ServerContext))
        self.Logger.PrintDebug("ChannelContext, %s" % (ChannelContext))
        self.Logger.PrintDebug("SearchShares, %s" % (SearchStr))
        SearchStr=string.lower(str(SearchStr))
        SearchStr=string.replace(SearchStr,' ','%')
        SearchStr=string.replace(SearchStr,'*','%')
    
        MaxFindResults = self.dbc.dbFetchRow('''
                select max_find_results from options''')
    
        NetworkID = self.dbc.dbFetchRow('''
                select network_id from networks
                where lower(network_name) like "%s"''' %
                (string.lower(ServerContext)))
    
        NumberFound = self.dbc.dbFetchRow('''
                select count(F.file_name)
                from file F, list_contents L, channels C,
                serving_nicks N
                where L.list_id = C.list_id
                and F.file_id = L.file_id
                and C.nick_id = N.nick_id
                and C.network_id = %s
                and lower(C.channel_name) = "%s"
                and lower(file_name) like "%%%s%%"''' %
                (NetworkID, string.lower(ChannelContext),SearchStr))
    
        FoundFiles = self.dbc.dbFetchAll('''
                select N.nick_name as ToNick,
                F.directory_id as DirID,
                F.file_id as FileID,
                F.file_name as FileName
                from file F, list_contents L, channels C, serving_nicks N
                where L.list_id = C.list_id
                and F.file_id = L.file_id
                and C.nick_id = N.nick_id
                and C.network_id = %s
                and lower(C.channel_name) = "%s"
                and lower(file_name) like "%%%s%%"
                limit %s''' %
                (NetworkID, string.lower(ChannelContext),SearchStr, MaxFindResults))
    
        if FoundFiles:
            channel=xchat.find_context(channel="%s" % (ChannelContext))
    
            if NumberFound > MaxFindResults:
                xchat.command("msg %s d ^j^ b Hello," %(FromNick))
                xchat.command("msg %s I have %d files that match your query." %
                            (FromNick, NumberFound))
                xchat.command("msg %s Here are %d, See my list to view them all." %
                            (FromNick, MaxFindResults))
            for file in FoundFiles:
                xchat.command("msg %s !%s %d-%s" % \
                        (FromNick, file["ToNick"],file["DirID"],file["FileName"]))
                self.Logger.PrintDebug("!%s %d-%s" %
                        (file["ToNick"],file["DirID"],file["FileName"]))
    
    def __init__(self, dbc, Logger, FromNick, ServerContext, \
                ChannelContext, SearchStr):
        self.dbc=dbc
        self.Logger=Logger
        self.FromNick=FromNick
        self.ServerContext=ServerContext
        self.ChannelContext=ChannelContext
        self.SearchStr=SearchStr
        self.FindFiles(self.FromNick, self.ServerContext, \
                self.ChannelContext, self.SearchStr)

