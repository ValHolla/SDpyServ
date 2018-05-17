
import gtk, gobject
from threading import Thread

class StatsTab(Thread):

    def BuildStatsView(self, columnNames, TreeModel):

        TreeView=self.builder.get_object('ViewPaneTree')
        ##  Clear the Tree
        TreeModel.clear()
        for col in TreeView.get_columns():
            TreeView.remove_column(col)
        TreeView.set_model(TreeModel)
        TreeSelection=TreeView.get_selection()
        TreeRenderer=gtk.CellRendererText()
        for i in range(len(columnNames)):
            (column, title, width, resize) = columnNames[i]
            column=gtk.TreeViewColumn(title, TreeRenderer, text=i)
            gtk.TreeViewColumn.set_sizing(column, 'GTK_TREE_VIEW_COLUMN_FIXED')
            gtk.TreeViewColumn.set_fixed_width(column, int(width))
            column.set_resizable(resize)
            TreeView.append_column(column)
        TreeView.show_all()
        return (TreeView, TreeModel, TreeSelection)

    def ResetStats(self):
        self.dbc.dbDeleteRow('''
        delete from stats''')
        self.dbc.dbInsertRow('''
        insert into stats
        (last_reset_date, list_requested, list_finished,
        files_requested, files_sent, cancelled_cps_small,
        cancelled_cps_large, cancelled_lost_nick, timeouts)
        values
        (date_format(now(), '%Y-%m-%d'),0,0,0,0,0,0,0,0)
        ''')
        self.dbc.dbDeleteRow('''
        delete from nick_stats''')
        self.dbc.dbDeleteRow('''
        truncate nick_served''')
        ## Reset the ViewPaneTree
        TreeView=self.builder.get_object('ViewPaneTree')
        for col in TreeView.get_columns():
            TreeView.remove_column(col)

    def UpdateStats(self):
        Stats=self.dbc.dbFetchAll('''
        select * from stats limit 1''')
        for Stat in Stats:
            self.builder.get_object('LastResetValue').set_text \
                    (str(Stat["last_reset_date"]))
            self.builder.get_object('ListRequestedValue').set_text \
                    (str(Stat["list_requested"]))
            self.builder.get_object('ListFinishedValue').set_text \
                    (str(Stat["list_finished"]))
            self.builder.get_object('FilesRequestedValue').set_text \
                    (str(Stat["files_requested"]))
            self.builder.get_object('FilesSentValue').set_text \
                    (str(Stat["files_sent"]))
            self.builder.get_object('CancelledLowCPSsmall').set_text \
                    (str(Stat["cancelled_cps_small"]))
            self.builder.get_object('CancelledLowCPSlarge').set_text \
                    (str(Stat["cancelled_cps_large"]))
            self.builder.get_object('CancelledLostNickValue').set_text \
                    (str(Stat["cancelled_lost_nick"]))
            self.builder.get_object('TimeoutValue').set_text \
                    (str(Stat["timeouts"]))
        ## Reset the ViewPaneTree
        TreeView=self.builder.get_object('ViewPaneTree')
        for col in TreeView.get_columns():
            TreeView.remove_column(col)

    def __init__(self, builder, dbc):
        self.builder = builder
        self.dbc = dbc
        self.UpdateStats()
