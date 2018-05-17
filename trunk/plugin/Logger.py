import xchat

class Logger():

    def PrintDebug(self,string):
        DBG=xchat.find_context(channel='}}__SDpyServ-Debug__{{')
        if self.debug == 1:
            DBG.prnt('\00304'+string+'\003')

    def __init__(self, debug):
        self.debug=debug

        if self.debug == 1:
            import traceback
            xchat.command('query }}__SDpyServ-Debug__{{')

