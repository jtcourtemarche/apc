#!/usr/bin/python

import wx
from crawler import APCCrawler

class MainFrame(wx.Frame):
    def __init__(self, parent, title, res=(1280, 720)):
        wx.Frame.__init__(self, parent, title=title, size=res, style=wx.DEFAULT_FRAME_STYLE  & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.file_menu = wx.Menu()
        self.file_menu.Append(wx.ID_OPEN, '&Open')

        self.run_menu = wx.Menu()
        self.run_menu.Append(wx.ID_NONE, '&Scrape Links [F5]')

        self.about_menu = wx.Menu()
        self.about_menu.Append(wx.ID_ABOUT, '&About')

        self.menubar = wx.MenuBar()
        self.menubar.Append(self.file_menu, '&File')
        self.menubar.Append(self.run_menu, '&Run')
        self.menubar.Append(self.about_menu, '&About')

        self.panel = wx.Panel(self, size=res)

        self.text_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, 'Verdana')
        self.header_font = wx.Font(13, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, 'Verdana')

        # Load logo
        self.logo = wx.Image(
            'static/img/logo.jpg',
            wx.BITMAP_TYPE_JPEG,
        )
        # Convert logo to bitmap so it is renderable 
        self.bitmap = wx.StaticBitmap(self.panel, -1, wx.BitmapFromImage(self.logo)) 

        self.control_label = wx.StaticText(self.panel, label='Enter links below:', size=(800, 15), pos=(0, 75))
        self.control_label.SetFont(self.header_font)

        self.links_control = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(800, res[1]-150), pos=(0,95))
        self.links_control.SetFont(self.text_font)
        self.links_control.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        #self.crumbs_name_control = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(800/2, 20), pos=(0,res[1]/1.5))
        #self.crumbs_url_control = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE, size=(800/2, 20), pos=(res[0]/2,res[1]/1.5))

        self.gauge = wx.Gauge(self.panel, style=wx.GA_HORIZONTAL, range=100)
        self.panel.SetFocus()
        
        self.SetMenuBar(self.menubar)
        self.Show(True)

    def on_key_down(self, event):
        if event.GetKeyCode() == 27:
            self.Close(True)
        elif event.GetKeyCode() == 344:
            # This should run the program
            for url in enumerate(self.links_control.GetValue().splitlines()):
                print '{0}/{1} Loading APC Links'.format(url[0]+1, len(self.links_control.GetValue().splitlines()))
                scraper = APCCrawler(url[1])
                print 'Parsing HTML'
                scraper.parse()
                self.gauge.SetValue(2/100)
                print 'Applying template'
                scraper.apply_template()
                self.gauge.SetValue(100)
            print 'Done'
        elif event.GetModifiers() == 2 and event.GetKeyCode() == 65:
            # Select all
            self.links_control.SelectAll()
        else:
            event.Skip()

def run():
    app = wx.App(False)
    frame = MainFrame(None, 'APC Crawler')
    app.MainLoop()
