import wx

from Kernel import *

_ = wx.GetTranslation


class JobSpooler(wx.Frame, Module):
    def __init__(self, *args, **kwds):
        # begin wxGlade: JobSpooler.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        Module.__init__(self)
        self.SetSize((661, 402))
        self.list_job_spool = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_list_drag, self.list_job_spool)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_item_rightclick, self.list_job_spool)
        # end wxGlade
        self.dirty = False
        self.update_buffer_size = False
        self.update_spooler_state = False
        self.update_spooler = False

        self.elements_progress = 0
        self.elements_progress_total = 0
        self.command_index = 0
        self.listener_list = None
        self.list_lookup = {}
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def initialize(self):
        self.device.close('window', self.name)
        self.Show()
        if self.device.is_root():
            for attr in dir(self):
                value = getattr(self, attr)
                if isinstance(value, wx.Control):
                    value.Enable(False)
            dlg = wx.MessageDialog(None, _("You do not have a selected device."),
                                   _("No Device Selected."), wx.OK | wx.ICON_WARNING)
            result = dlg.ShowModal()
            dlg.Destroy()
            return
        self.device.listen('spooler;queue', self.on_spooler_update)
        self.refresh_spooler_list()

    def shutdown(self, channel):
        self.Close()

    def on_close(self, event):
        self.device.remove('window', self.name)
        self.device.unlisten('spooler;queue', self.on_spooler_update)
        event.Skip()  # Call destroy as regular.

    def __set_properties(self):
        # begin wxGlade: JobSpooler.__set_properties
        self.SetTitle("Spooler")
        self.list_job_spool.SetToolTip("List and modify the queued operations")
        self.list_job_spool.AppendColumn("#", format=wx.LIST_FORMAT_LEFT, width=29)
        self.list_job_spool.AppendColumn("Name", format=wx.LIST_FORMAT_LEFT, width=90)
        self.list_job_spool.AppendColumn("Status", format=wx.LIST_FORMAT_LEFT, width=73)
        self.list_job_spool.AppendColumn("Device", format=wx.LIST_FORMAT_LEFT, width=53)
        self.list_job_spool.AppendColumn("Type", format=wx.LIST_FORMAT_LEFT, width=41)
        self.list_job_spool.AppendColumn("Speed", format=wx.LIST_FORMAT_LEFT, width=77)
        self.list_job_spool.AppendColumn("Settings", format=wx.LIST_FORMAT_LEFT, width=82+70)
        self.list_job_spool.AppendColumn("Time Estimate", format=wx.LIST_FORMAT_LEFT, width=123)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: JobSpooler.__do_layout
        spool_sizer = wx.BoxSizer(wx.VERTICAL)
        spool_sizer.Add(self.list_job_spool, 8, wx.EXPAND, 0)
        self.SetSizer(spool_sizer)
        self.Layout()
        # end wxGlade

    def on_list_drag(self, event):  # wxGlade: JobSpooler.<event_handler>
        event.Skip()

    def on_item_rightclick(self, event):  # wxGlade: JobSpooler.<event_handler>
        event.Skip()

    def refresh_spooler_list(self):
        def name_str(e):
            try:
                return e.__name__
            except AttributeError:
                return str(e)

        self.list_job_spool.DeleteAllItems()
        if len(self.device.spooler._queue) > 0:
            # This should actually process and update the queue items.
            i = 0
            for e in self.device.spooler._queue:
                m = self.list_job_spool.InsertItem(i, "#%d" % i)
                if m != -1:
                    self.list_job_spool.SetItem(m, 1, name_str(e))
                    try:
                        self.list_job_spool.SetItem(m, 2, e.status)
                    except AttributeError:
                        pass
                    self.list_job_spool.SetItem(m, 3, self.device.device_name)
                    settings = []
                    if isinstance(e, EngraveOperation):
                        self.list_job_spool.SetItem(m, 4, _("Engrave"))
                    if isinstance(e, CutOperation):
                        self.list_job_spool.SetItem(m, 4, _("Cut"))
                    if isinstance(e, RasterOperation):
                        self.list_job_spool.SetItem(m, 4, _("Raster"))
                    try:
                        self.list_job_spool.SetItem(m, 5, _("%.1fmm/s") % (e.speed))
                    except AttributeError:
                        pass
                    settings = list()
                    try:
                        settings.append(_("power=%g") % (e.power))
                    except AttributeError:
                        pass
                    try:
                        settings.append(_("step=%d") % (e.raster_step))
                    except AttributeError:
                        pass
                    try:
                        settings.append(_("overscan=%d") % (e.overscan))
                    except AttributeError:
                        pass
                    self.list_job_spool.SetItem(m, 6, " ".join(settings))
                    try:
                        self.list_job_spool.SetItem(m, 7, e.time_estimate)
                    except AttributeError:
                        pass

                i += 1

    def on_tree_popup_clear(self, element):
        def delete(event):
            self.device.spooler.clear_queue()
            self.refresh_spooler_list()

        return delete

    def on_tree_popup_delete(self, element):
        def delete(event):
            self.device.spooler.remove(element)
            self.refresh_spooler_list()

        return delete

    def on_spooler_update(self, value):
        self.update_spooler = True
        self.refresh_spooler_list()

