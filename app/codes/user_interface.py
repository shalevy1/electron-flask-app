import wx
#useful import




class Form(wx.Panel):
    ''' The Form class is a wx.Panel that creates a bunch of controls
        and handlers for callbacks. Doing the layout of the controls is
        the responsibility of subclasses (by means of the doLayout()
        method). '''

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.createControls()
        self.bindEvents()
        self.doLayout()

    def createControls(self):
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.saveButton = wx.Button(self, label="Save")
        self.nameLabel = wx.StaticText(self, label="Fichier Principal")
        self.bomFileChooser = wx.FilePickerCtrl(self,
            wildcard="CFG files (*.XLSX)|*.XLSX")
        self.ressourceLabel = wx.StaticText(self, label="Fichier des Ressources")
        self.ressourceFileChooser = wx.FilePickerCtrl(self)
        self.interOpLabel = wx.StaticText(self, label="Fichier Pour Interoperations")
        self.interOpFileChooser = wx.FilePickerCtrl(self)
        self.excludedLabel = wx.StaticText(self, label="Produits à exclure ")
        self.excludedFileChooser = wx.FilePickerCtrl(self)
        self.productLabel = wx.StaticText(self, label="Produits à calculer  ")
        self.productFileChooser = wx.FilePickerCtrl(self)

    def bindEvents(self):
        for control, event, handler in \
            [(self.saveButton, wx.EVT_BUTTON, self.onSave),
            (self.bomFileChooser, wx.EVT_FILEPICKER_CHANGED, self.onBomFileSelected)
            ]:
            control.Bind(event, handler)

    def doLayout(self):
        ''' Layout the controls that were created by createControls().
            Form.doLayout() will raise a NotImplementedError because it
            is the responsibility of subclasses to layout the controls. '''
        raise NotImplementedError

    # Callback methods:

    def onBomFileSelected(self, event):
        bom_file = self.bomFileChooser.GetPath()
        self.__log('user select file : {}'.format(bom_file))
        try:
            pass
        except Exception as e:
            raise e


    def onRessourcesFileSelected(self, event):
        bom_file = self.bomFileChooser.GetPath()
        self.__log('user select file : {}'.format(bom_file))
        try:
            pass
        except Exception as e:
            raise e


    def onInterOperationFileSelected(self, event):
        bom_file = self.bomFileChooser.GetPath()
        self.__log('user select file : {}'.format(bom_file))
        try:
            pass
        except Exception as e:
            raise e


    def onExcludedFileSelected(self, event):
        bom_file = self.bomFileChooser.GetPath()
        self.__log('user select file : {}'.format(bom_file))
        try:
            pass
        except Exception as e:
            raise e


    def onProductFileSelected(self, event):
        bom_file = self.bomFileChooser.GetPath()
        self.__log('user select file : {}'.format(bom_file))
        try:
            pass
        except Exception as e:
            raise e



    def onSave(self,event):
        self.__log('User clicked on button with id %d'%event.GetId())


    # Helper method(s):

    def __log(self, message):
        ''' Private method to append a string to the logger text
            control. '''
        self.logger.AppendText('%s\n'%message)


class FormWithAbsolutePositioning(Form):
    def doLayout(self):
        ''' Layout the controls by means of absolute positioning. '''
        for control, x, y, width, height in \
                [(self.logger, 400, 20, 200, 300),
                 (self.nameLabel, 20, 67, -1, -1),
                 (self.bomFileChooser, 150, 60, 200, -1),
                 (self.ressourceLabel, 20, 92, -1, -1),
                 (self.ressourceFileChooser, 150, 85, 200, -1),
                 (self.interOpLabel, 20, 117, -1, -1),
                 (self.interOpFileChooser, 150, 110, 200, -1),
                 (self.excludedLabel, 20, 142, -1, -1),
                 (self.excludedFileChooser, 150, 135, 200, -1),
                 (self.productLabel, 20, 167, -1, -1),
                 (self.productFileChooser, 150, 160, 200, -1),
                 (self.saveButton, 200, 300, -1, -1)]:
            control.SetDimensions(x=x, y=y, width=width, height=height)


class FrameWithForms(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(*args, **kwargs)
        notebook = wx.Notebook(self)
        form1 = FormWithAbsolutePositioning(notebook)
        notebook.AddPage(form1, 'Selectionner les Fichiers')
        # We just set the frame to the right size manually. This is feasible
        # for the frame since the frame contains just one component. If the
        # frame had contained more than one component, we would use sizers
        # of course, as demonstrated in the FormWithSizer class above.
        self.SetClientSize(notebook.GetBestSize())


if __name__ == '__main__':
    app = wx.App(0)
    frame = FrameWithForms(None, title='Bio Rad PRI')
    frame.Show()
    app.MainLoop()
