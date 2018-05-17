import xchat

class SDpyServQueues():

    def CheckQueue(self, ToNick, FromNick, ServerContext, ChannelContext):
        PrintDebug("CheckQueue")

    def DeleteFromQueue(self, QueuedFile, ToNick, FromNick,\
                        ServerContext, ChannelContext):
        PrintDebug("DeleteFromQueue - Queued File = %s" % (QueuedFile))

    def __init__(self, dbc):
        self.dbc=dbc
        
