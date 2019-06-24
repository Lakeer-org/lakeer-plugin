from PyQt5.QtWidgets import QProgressDialog, QProgressBar, QApplication

class ProgressBar:
    '''
    Progress bar display on loading data
    '''
    def __init__(self, total):
        # Adding dialog which will pop-up on show
        self.dialog = QProgressDialog()
        self.dialog.setWindowTitle("Progress")
        self.dialog.setLabelText("Loading 0 of "+str(total))
        self.dialog.setMinimumWidth(300)

        #Define Progress bar with 0 value and max value to 100
        self.bar = QProgressBar(self.dialog)
        self.bar.setTextVisible(True)
        self.bar.setValue(0)
        self.dialog.setBar(self.bar)
        self.bar.setMaximum(100)
        self.dialog.show()
        self.total_value = total
        self.update_progress(0)
        QApplication.processEvents()

    def update_progress(self, progress_value):
        '''
        Update the value of the progress value in the pop-up dialogue and also update the text.
        :param progress_value:
        :return:
        '''
        self.bar.setValue((progress_value/self.total_value)*100)
        self.dialog.setLabelText("Loading "+ str(progress_value) + ' of '+ str(self.total_value))
        QApplication.processEvents()