#region Simple Click Me
# import gi
# gi.require_version('Gtk', '4.0')
# from gi.repository import Gtk
#
# class MyWindow(Gtk.ApplicationWindow):
#     def __init__(self, app):
#         super().__init__(title="Hello GTK", application=app)
#         self.set_default_size(200, 100)
#         button = Gtk.Button(label="Click Me")
#         button.connect("clicked", self.on_button_clicked)
#         self.set_child(button)
#
#     def on_button_clicked(self, widget):
#         print("Button Clicked!")
#
# class MyApp(Gtk.Application):
#     def do_activate(self):
#         win = MyWindow(self)
#         win.show()
#
#     def do_startup(self):
#         Gtk.Application.do_startup(self)
#
# app = MyApp()
# app.run()
#endregion


#region Web Browser
# import gi
# gi.require_version('Gtk', '4.0')
# gi.require_version('WebKit2', '5.0')
# from gi.repository import Gtk, WebKit2
#
# class BrowserWindow(Gtk.ApplicationWindow):
#     def __init__(self, app):
#         super().__init__(title="Embedded Web Browser", application=app)
#         self.set_default_size(800, 600)
#
#         # Create a WebKit web view to show a web page
#         self.webview = WebKit2.WebView()
#         self.set_child(self.webview)
#         self.webview.load_uri("https://www.example.com")
#
# class BrowserApp(Gtk.Application):
#     def do_activate(self):
#         win = BrowserWindow(self)
#         win.show()
#
#     def do_startup(self):
#         Gtk.Application.do_startup(self)
#
# app = BrowserApp()
# app.run()
#endregion