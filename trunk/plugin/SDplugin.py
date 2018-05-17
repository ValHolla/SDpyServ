#!/usr/bin/python
# 
# $Id: $
#
import string, ConfigParser
import os, re, sys 
import xchat
from stat import *

BaseDir = "/home/mike/Devel/SDpyServ"
PluginDir = "%s/plugin" % (BaseDir)
ConfigFileName = "%s/etc/SDpyServ.cfg" % (BaseDir)

# Add the PluginDir to the path so we can find our class files
sys.path.append(PluginDir)

from DbCalls import DbCalls
from ProcessList import ProcessList
from QueueCommands import SDpyServQueues
from SearchList import SearchList
from Logger import Logger

__module_name__ = "SDpyServ"
__module_version__ = "0.1 beta"
__module_description__ = "A DCC file server for xChat"

global Logger
global dbc

# Read the config file containing DB information
config=ConfigParser.ConfigParser()
configFile = open(ConfigFileName)
config.readfp(configFile)

# Initialize the DB
dbc=DbCalls(config)

## Debug -- Set to non '0'(zero) to disable
_debug_ = 1 

Logger=Logger(_debug_)

Logger.PrintDebug("Loading %s, Version %s" % 
        (__module_name__, __module_version__))

def ProcessRequest(RequestedFile, ToNick, FromNick, \
                   ServerContext, ChannelContext):
    global Logger
    Logger.PrintDebug("ProcessRequest")

def InspectMessage(word, word_eol, userdata=None):
    global dbc
    global Logger
    ServeNick='ValHolla'
    ServeNick=ServeNick.lower()

    ServerContext=xchat.get_info("server")   ## Server The Message Came From
    ChannelContext=xchat.get_info("channel") ## Channel The Message Came From
    FromNick=word[0][1:word[0].index('!')]   ## The Nick Sending The Message
    word[3]=word[3][1:]         ## Strip off leading colon from The Message
    command=word[3].lower()     ## Set The Message to all lowercase
    
    ToNick=word[3][1:]  ## Strip the first character '! or @' ToNick
                        ## ToNick is the Nick the Message is directed to
                        ## ToNick may still contain '-que' and '-remove'
                        ## We will handle that below

    ## Commands we are looking for
    RequestCommand="!%s" % (ServeNick)
    ListCommand="@%s" % (ServeNick)
    CheckQueueCommand="%s-que" % (ListCommand)
    DeleteQueueCommand="@%s-remove" % (ServeNick)
    FindCommand="@find"

    if (command == ListCommand):
        ProcessListCommand(ToNick, FromNick, ServerContext, ChannelContext)
        return xchat.EAT_ALL
    
    if (command == CheckQueueCommand):
        ToNick=re.sub("-que","", ToNick) ## strip '-que' from ToNick
        CheckQueue(ToNick, FromNick, ServerContext, ChannelContext)
        return xchat.EAT_ALL
    
    if (command == DeleteQueueCommand):
        ToNick=re.sub("-remove","", ToNick) ## strip '-remove' from ToNick
        QueuedFile=None
        if (len(word) > 4):
            QueuedFile=word_eol[4]
        DeleteFromQueue(QueuedFile, ToNick, FromNick, \
                        ServerContext, ChannelContext)
        return xchat.EAT_ALL
    
    if (command == RequestCommand):
        if (len(word) > 4):
            RequestedFile=word_eol[4]
            ProcessRequest(RequestedFile, ToNick, FromNick, \
                           ServerContext, ChannelContext)
            return xchat.EAT_PLUGIN
        else:
            return xchat.EAT_NONE
    
    if (command == FindCommand):
        if (len(word) > 4):
            SearchString=word_eol[4]
            SearchList(dbc, Logger, FromNick, \
                         ServerContext, ChannelContext, SearchString)
            return xchat.EAT_PLUGIN
        else:
            return xchat.EAT_NONE

    return xchat.EAT_NONE

## -- Server Hooks -- ##
xchat.hook_server('PRIVMSG', InspectMessage, priority=xchat.PRI_HIGHEST)
