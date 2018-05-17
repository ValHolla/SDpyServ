#!/usr/bin/python

## Base Classes
import gtk
import gobject
import threading, thread
import ConfigParser, os, sys

## My Classes
from InitializeGui import InitializeGui
from ListTab import ListTab
from ChannelTab import ChannelTab
from DbCalls import DbCalls
from ErrorDialogs import ErrorDialogs
from Callbacks import Callbacks
from StatsTab import StatsTab

def main():
    gobject.threads_init()
    gtk.gdk.threads_init()
    SDpyServVersion='0.1'

    GuiOptions={
        'ServingDirectory': None,
        'SendSlots': None, 'DynamicSlots': None,
        'FilesInQueue': None, 'QueueFull': None,
        'MaxFindNum': None, 'SmallLowCps': None,
        'LargeLowCps': None, 'LargeFileSize': None,
        'QueueListCheck': None, 'MaxListQueue': None,
        'SendCtcpCheck': None, 'SendCtcpFreq': None,
        'RandomPlayCheck': None, 'RandomPlayFreq': None,
        'EnableFindCheck': None, 'radioLogging': None,
        'ServerPriority': None, 'ZipListCheck': None,
        'ExtentionEntry': None }

    PriorityList = {
        'radioNormal': 0,
        'radioServer': 1,
        'radioServerOnlySilent': 2,
        'radioServerOnly': 3 }

    LoggingList = {
        'radioNormalLog': 0,
        'radioSeperateLog': 1,
        'radioFileLog': 2 }

    config=ConfigParser.ConfigParser()
    configFile = open('etc/SDpyServ.cfg')
    config.readfp(configFile)

    builder = gtk.Builder()
    builder.add_from_file("share/SDpyServ.ui")
    About=builder.get_object('AboutWindow')
    About.set_property('version', SDpyServVersion)
    sdError=ErrorDialogs(builder)

    dbc=DbCalls(builder,config,sdError)
        
    listTab=ListTab(builder,dbc)
    channelTab=ChannelTab(builder,dbc)
    statsTab=StatsTab(builder,dbc)

    ## Initialize Gui Values
    InitializeGui(builder, dbc, GuiOptions, \
                  LoggingList, PriorityList)
    ## Connect All Signals
    pyServCB=Callbacks(builder, dbc, \
                       GuiOptions, LoggingList, listTab, \
                       channelTab, statsTab, PriorityList, sdError)
    builder.connect_signals(pyServCB)
    ## Show the main window
    pyServWindow = builder.get_object("pyServWin")
    pyServWindow.show()
    ## Loop for and wait for events
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave()
    ## Close the DB connection
    dbc.dbCloseConnection()

if __name__ == "__main__":
    main()
