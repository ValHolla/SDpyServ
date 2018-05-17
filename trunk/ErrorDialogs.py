
class ErrorDialogs():
    def UserError(self, message=None):
        ErrDlg=self.builder.get_object('ErrorDialog')
        ErrDlg.format_secondary_text(message)
        ErrDlg.show_all()

    def FatalError(self, message=None):
        ErrDlg=self.builder.get_object('FatalErrorDialog')
        ErrDlg.format_secondary_text(message)
        ErrDlg.show_all()

    def __init__(self, builder):
        self.builder = builder
