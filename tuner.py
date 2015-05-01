#!/usr/bin/env python
# -*- coding: UTF8 -*-

# tuner.py
# version 1.9

from gi.repository import Gtk, GObject, Gdk
from subprocess import Popen
from collections import deque
from signal import SIGINT

#########################################################################
# class Note
#########################################################################
# Defines note names and frequencies
#########################################################################
class Note():

    INDEX_FR_NAME, INDEX_EN_NAME, INDEX_FREQ = range(3)

    keys = [["Do", "C", "32.7"], ["Do♯","C♯", "34.65"], ["Ré", "D", "36.71"],
            ["Ré♯","D♯", "38.89"], ["Mi", "E", "41.2"], ["Fa", "F", "43.65"],
            ["Fa♯","F♯", "46.25"], ["Sol", "G", "49"], ["Sol♯","G♯", "51.91"],
            ["La", "A", "55"], ["La♯","A♯", "58.27"], ["Si", "B", "61.74"],
            ["Do", "C", "65.41"], ["Do♯","C♯", "69.3"], ["Ré", "D", "73.42"],
            ["Ré♯","D♯", "77.78"], ["Mi", "E", "82.41"], ["Fa", "F", "87.31"],
            ["Fa♯","F♯", "92.5"], ["Sol", "G", "98"], ["Sol♯","G♯", "103.83"],
            ["La", "A", "110"], ["La♯","A♯", "116.54"], ["Si", "B", "123.47"],
            ["Do", "C", "130.81"], ["Do♯","C♯", "138.59"], ["Ré", "D", "146.83"],
            ["Ré♯","D♯", "155.56"], ["Mi", "E", "164.81"], ["Fa", "F", "174.61"],
            ["Fa♯","F♯", "185"], ["Sol", "G", "196"], ["Sol♯","G♯", "207.65"],
            ["La", "A", "220"], ["La♯","A♯", "233.08"], ["Si", "B", "246.94"],
            ["Do", "C", "261.63"], ["Do♯","C♯", "277.18"], ["Ré", "D", "293.66"],
            ["Ré♯","D♯", "311.13"], ["Mi", "E", "329.63"], ["Fa", "F", "349.23"],
            ["Fa♯","F♯", "369.99"], ["Sol", "G", "392"], ["Sol♯","G♯", "415.3"],
            ["La", "A", "440"], ["La♯","A♯", "466.16"], ["Si", "B", "493.88"],
            ["Do", "C", "523.25"], ["Do♯","C♯", "554.37"], ["Ré", "D", "587.33"],
            ["Ré♯","D♯", "622.25"], ["Mi", "E", "659.26"], ["Fa", "F", "698.46"],
            ["Fa♯","F♯", "739.99"], ["Sol", "G", "783.99"], ["Sol♯","G♯", "830.61"],
            ["La", "A", "880"], ["La♯","A♯", "932.33"], ["Si", "B", "987.77"],
            ["Do", "C", "1046.5"], ["Do♯","C♯", "1108.73"], ["Ré", "D", "1174.66"],
            ["Ré♯","D♯", "1244.51"], ["Mi", "E", "1318.51"], ["Fa", "F", "1396.91"],
            ["Fa♯","F♯", "1479.98"], ["Sol", "G", "1567.98"], ["Sol♯","G♯", "1661.22"],
            ["La", "A", "1760"], ["La♯","A♯", "1864.66"], ["Si", "B", "1975.53"],
            ["Do", "C", "2093"], ["Do♯","C♯", "2217.46"], ["Ré", "D", "2349.32"],
            ["Ré♯","D♯", "2489.02"], ["Mi", "E", "2637.02"], ["Fa", "F", "2793.83"],
            ["Fa♯","F♯", "2959.96"], ["Sol", "G", "3135.96"], ["Sol♯","G♯", "3322.44"],
            ["La", "A", "3520"], ["La♯","A♯", "3729.31"], ["Si", "B", "3951.07"],
            ["Do", "C", "4186.01"], ["Do♯","C♯", "4434.92"], ["Ré", "D", "4698.64"],
            ["Ré♯","D♯", "4978.03"], ["Mi", "E", "5274.04"], ["Fa", "F", "5587.65"],
            ["Fa♯","F♯", "5919.91"], ["Sol", "G", "6271.93"], ["Sol♯","G♯", "6644.88"],
            ["La", "A", "7040"], ["La♯","A♯", "7458.62"], ["Si", "B", "7902.13"]]

#########################################################################
# class Note_selection_dialog
#########################################################################
# Custom widget to pick a frequency
#########################################################################
class Note_selection_dialog(Gtk.Dialog):
        
    #####################################################################
    # Key pressed
    #####################################################################
    def _key_pressed(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if 'Escape' == key:
            self.emit('response', Gtk.ResponseType.CANCEL)
        elif 'Return' == key:
            self._note_selected()

    #####################################################################
    # Double-click
    #####################################################################
    def _double_click(self, widget, event):
        if event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS :
            self._note_selected()

    #####################################################################
    # Note selected
    #####################################################################
    def _note_selected(self):
        # Get selection
        select = self._tree.get_selection()
        model, treeiter = select.get_selected()
        if treeiter is not None:
            self._index = model.get_path(treeiter).get_indices()[0] 
            self.emit('response', Gtk.ResponseType.OK)

    #####################################################################
    # Get index
    #####################################################################
    def get_index(self):
        return self._index
    
    #####################################################################
    # Init
    #####################################################################
    def __init__(self, title, index, notestyle_index):

        # Notes
        store = (Gtk.ListStore(str, str, str))
        for freq in Note.keys:
            store.append(freq)

        # Window
        #GObject.GObject.__init__(self, title)
        GObject.GObject.__init__(self)
        self.set_modal(True)
        self.set_title(title)
        self.set_size_request(150,600)
        self.set_border_width(10)
        self.connect("key-press-event", self._key_pressed)
        # Position window under mouse cursor
        # Should be replaced with something better for keyboard use
        self.set_position(Gtk.WindowPosition.MOUSE)

        # Treeview
        self._tree = Gtk.TreeView(store)
        self._tree.connect("button-press-event", self._double_click) 
        # Select current freq
        self._tree.set_cursor(Gtk.TreePath(index), None, False)
        # Scroll to current freq
        self._tree.scroll_to_cell(index, use_align=True, row_align=0.5)
        
        # Name
        self._renderer = Gtk.CellRendererText()
        self._column = Gtk.TreeViewColumn("Note")
        self._column.pack_start(self._renderer, True)
        self._column.add_attribute(self._renderer, "text", notestyle_index)
        self._tree.append_column(self._column)

        # Freq
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Frequence", renderer, text=2)
        self._tree.append_column(column)
        
        # Scroller
        scroll = Gtk.ScrolledWindow()
        scroll.add(self._tree)
        self.vbox.pack_start(scroll, True, True, 0)
        
        # Show all
        ##########
        self._tree.show()
        scroll.show()
        self.show()

#########################################################################
# class Key 
#########################################################################
# Each instance is a key on the board, along with buttons to select 
# another note
#########################################################################
class Key(Gtk.Box):

    #####################################################################
    # Increment freq
    #####################################################################
    def increment_freq(self, *args):
        if self._index < len(Note.keys) - 1:
            self._index = self._index + 1
            self.set_label()
        if self._index is len(Note.keys) - 1 :
            self._button_up.set_sensitive(False)
        self._button_down.set_sensitive(True)
        self._accordeur.keys_modified()
        
    #####################################################################
    # Decrement freq
    #####################################################################
    def decrement_freq(self, *args):
        if self._index > 0:
            self._index = self._index - 1
            self.set_label()
        if self._index is 0:
            self._button_down.set_sensitive(False)
        self._button_up.set_sensitive(True)
        self._accordeur.keys_modified()
        
    #####################################################################
    # Select note
    #####################################################################
    def _select_note(self, widget):

        # Create note selection dialog
        note_selector = Note_selection_dialog("Select note", 
                                            self._index,
                                            self._accordeur.get_notestyle())
        # Wait for response
        response = note_selector.run()
              
        # If new freq selected
        if response == Gtk.ResponseType.OK:
            # Get freq index from dialog
            self._index = note_selector.get_index()
            # Set label
            self.set_label()
            # Set buttons sensitivity accordingly
            if self._index is 0:
                self._button_up.set_sensitive(True)
                self._button_down.set_sensitive(False)
            elif self._index is (len(Note.keys) - 1 ):
                self._button_up.set_sensitive(False)
                self._button_down.set_sensitive(True)
            else:
                self._button_up.set_sensitive(True)
                self._button_down.set_sensitive(True)
            self._accordeur.keys_modified()
        
        # Destroy widget
        note_selector.destroy()
    
    #####################################################################
    # Get freq
    #####################################################################
    def get_freq(self):
        return Note.keys[self._index][Note.INDEX_FREQ]

    #####################################################################
    # Get index
    #####################################################################
    def get_index(self):
        return self._index

    #####################################################################
    # Set label
    #####################################################################
    def set_label(self):
        # Get notestyle
        notestyle = self._accordeur.get_notestyle()
       
        # Set button label
        self._pick_button.set_label(Note.keys[self._index][notestyle])

    #####################################################################
    # Enable
    #####################################################################
    def enable(self):
        self._play_button.set_sensitive(True)

    #####################################################################
    # Disable
    #####################################################################
    def disable(self):
        self._play_button.set_sensitive(False)

    #####################################################################
    # Play
    #####################################################################
    def _play(self, *args):
        self._accordeur.add_note_to_queue(None, Note.keys[self._index][Note.INDEX_FREQ])

    #####################################################################
    # Init
    #####################################################################
    def __init__(self, index, accordeur):

        self._index = index
        self._accordeur = accordeur
        
        # Vertical box
        ##############
        GObject.GObject.__init__(self, spacing=5, orientation=Gtk.Orientation.VERTICAL)

        # Add play button
        self._play_button = Gtk.Button()
        self._play_button.set_size_request(40, 40)
        self._play_button.set_label(u"\u266A")
        self.pack_start(self._play_button, True, True, 0)
        self._play_button.show()

        # Add pick freq button
        self._pick_button = Gtk.Button()
        self._pick_button.set_size_request(10, 40)
        self.pack_start(self._pick_button, True, True, 0)
        self._pick_button.show()

        # Add up arrow
        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.UP, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label=u"\u266F")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_up = Gtk.Button()
        self._button_up.add(HBox_arrow)
        self.pack_start(self._button_up, False, True, 0)
        HBox_arrow.show()
        self._button_up.show()

        # Add down arrow
        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.DOWN, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label=u"\u266D")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_down = Gtk.Button()
        self._button_down.add(HBox_arrow)
        self.pack_start(self._button_down, False, True, 0)
        HBox_arrow.show()
        self._button_down.show()
        
        # Connect handlers
        ##################
        self._handler = self._play_button.connect("clicked", self._play)
        self._button_up.connect("clicked", self.increment_freq)
        self._button_down.connect("clicked", self.decrement_freq)
        self._pick_button.connect("clicked", self._select_note)

        # Show all
        ##########
        self.set_label()
        self.show()

#########################################################################
# class Tuner
#########################################################################
class Tuner:

    # Define backends
    _BEEP, _SOX_SINE, _SOX_PLUCK = range(3)

    #####################################################################
    # Play note
    #####################################################################
    def _play_note(self, freq):
        self._note_playing = True
        self._disable_buttons()
        try:
            if self._backend is self._BEEP:
                self._beep_process = \
                    Popen(['beep',
                           '-f %s' % freq, 
                           '-l %s' % (1000 * self._beep_length)])
            elif self._backend is self._SOX_SINE:
                self._beep_process = \
                    Popen(['play', '-n', 
                           'synth', '1', 
                           'sine', '%s' % freq, 
                           'repeat', '%s' % (self._beep_length - 1)])
            elif self._backend is self._SOX_PLUCK:
                self._beep_process = \
                    Popen(['play', '-n', 
                           'synth', '1', 
                           'pluck', '%s' % freq, 
                           'repeat', '%s' % (self._beep_length - 1)])
        except OSError:
            self._missing_package_error(self._backend)
            self._note_playing = False
        # Set polling in idle to reconnect handles
        else:
            GObject.idle_add(self._poll_beep_in_progress)

    #####################################################################
    # Stop playback
    #####################################################################
    def _stop_playback_request(self, *args):
        GObject.idle_add(self._stop_playback)

    #####################################################################
    # Stop playback
    #####################################################################
    def _stop_playback(self):
        self._beep_queue.clear()
        # If process still alive (or zombie)
        if self._note_playing :
            # Send signal
            try:
                self._beep_process.send_signal(SIGINT)
            except OSError:
                print ("Could not SIGINT process")

    #####################################################################
    # Missing package error
    #####################################################################
    def _missing_package_error(self, package):
        
        # CLI
        if package is self._BEEP:
            print ("Oops!  Apparemment, beep n'est pas installé. (http://johnath.com/beep/)")
        elif (package is self._SOX_SINE) or (package is self._SOX_PLUCK):
            print ("Oops!  Apparemment, sox n'est pas installé. (http://sox.sourceforge.net/)")
        print ("Un paquet est sans doute disponible pour votre distribution.")
        
        # GUI
        if package is self._BEEP:
            dialog = Gtk.Dialog(title="beep n'est pas installé", \
                                parent=None, \
                                flags=Gtk.DialogFlags.MODAL, \
                                buttons=(Gtk.STOCK_DIALOG_ERROR, \
                                Gtk.ResponseType.CLOSE))
            error_message = "Oops!  Apparemment, beep n'est pas installé. " \
            + "(http://johnath.com/beep/)\n" \
            + "Un paquet est sans doute disponible pour votre distribution."
        elif (package is self._SOX_SINE) or (package is self._SOX_PLUCK):
            dialog = Gtk.Dialog(title="sox n'est pas installé", \
                                parent=None, \
                                flags=Gtk.DialogFlags.MODAL, \
                                buttons=(Gtk.STOCK_DIALOG_ERROR, \
                                Gtk.ResponseType.CLOSE))
            error_message = "Oops!  Apparemment, sox n'est pas installé. " \
            + "(http://sox.sourceforge.net/)\n" \
            + "Un paquet est sans doute disponible pour votre distribution."
        label = Gtk.Label(label=error_message)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        response = dialog.run()
        if (Gtk.ResponseType.CLOSE == response or Gtk.ResponseType.DELETE_EVENT == response):
            dialog.destroy()

    #####################################################################
    # Add note to queue
    #####################################################################
    def add_note_to_queue(self, widget, freq):
        self._beep_queue.append(freq)

    #####################################################################
    # Play note in queue
    #####################################################################
    def _play_note_from_queue(self):
        # If no playback ongoing
        if not self._note_playing :
            # If Queue not empty
            if self._beep_queue:
                # Play note from queue
                self._play_note(self._beep_queue.popleft())
        return True

    #####################################################################
    # Play all
    #####################################################################
    def _play_all(self, *args):
        # Add all notes ont keyboard to queue
        for key in self._buttons:
            self.add_note_to_queue(None, key.get_freq())

    #####################################################################
    # Add key
    #####################################################################
    def _add_key(self, widget, hbox, index=None):
        # If no freq specified, use same as rightmost
        if index is None:
            index = self._buttons[-1].get_index()
        
        # Create new key
        key = Key(index, self)
        hbox.pack_start(key, True, True, 0)
        self._buttons.append(key)
        
        # Refresh button and flag states
        self._button_rem.set_sensitive(True)
        self.keys_modified()

    #####################################################################
    # Remove key
    #####################################################################
    def _rem_key(self, *args):
        if len(self._buttons):
            self._buttons.pop().destroy()
        if not len(self._buttons):
            self._button_rem.set_sensitive(False)
        self.keys_modified()
        
    #####################################################################
    # Get note style
    #####################################################################
    def get_notestyle(self):
        return self._notestyle

    #####################################################################
    # Set note style
    #####################################################################
    def _set_notestyle(self, widget, notestyle):
        self._notestyle = notestyle
        for key in self._buttons:
            key.set_label()

    #####################################################################
    # Set backend
    #####################################################################
    def _set_backend(self, widget, backend):
        self._backend = backend

    #####################################################################
    # Set beep length
    #####################################################################
    def _set_beep_length (self, widget, beep_length_spin):
        self._beep_length = beep_length_spin.get_value()

    #####################################################################
    # Tune up
    #####################################################################
    def _tune_up (self, *args):
        # Tune all keys one semitone up
        for key in self._buttons:
            key.increment_freq()
        self.keys_modified()

    #####################################################################
    # Tune down
    #####################################################################
    def _tune_down (self, *args):
        # Tune all keys one semitone down
        for key in self._buttons:
            key.decrement_freq()
        self.keys_modified()

    #####################################################################
    # Disable buttons
    #####################################################################
    def _disable_buttons(self):
        # Disable all keys
        for key in self._buttons:
            key.disable()
        
        # Enable stop playback button and disable the others
        self._reset_button.set_sensitive(False)
        self._play_all_button.set_sensitive(False)
        self._stop_playback_button.set_sensitive(True)

    #####################################################################
    # Enable buttons
    #####################################################################
    def _enable_buttons(self):
        # Enable all keys
        for key in self._buttons:
            key.enable()
        
        # Disable stop playback button and enable the others
        if self._keys_modified :
            self._reset_button.set_sensitive(True)
        self._play_all_button.set_sensitive(True)
        self._stop_playback_button.set_sensitive(False)

    #####################################################################
    # Reset keys
    #####################################################################
    def _reset_keys (self, widget, hbox):
        # Disable keys modified flag
        self._keys_modified = False
        
        # Remove all keys
        for i in range(len(self._buttons)):
            self._rem_key()
        
        # Set default keys
        for i in range (len(self._default_keys)):
            self._add_key(None, hbox, self._default_keys[i])
        
        # Disable reset button
        self._reset_button.set_sensitive(False)
        
    #####################################################################
    # Keys modified
    #####################################################################
    def keys_modified (self):
        # When the keyboard is modified, set the flag...
        self._keys_modified = True
        
        # ... and set reset button sensitive
        self._reset_button.set_sensitive(True)

    #####################################################################
    # Poll beep in progress
    #####################################################################
    def _poll_beep_in_progress (self):
        # Process still running -> return true to keep polling
        if self._beep_process.poll() is None:
            return True
        # If no more note in queue, enable buttons. Otherwise, don't.
        # (this avoids glitches when enabling/disabling instantly)
        if not self._beep_queue:
            self._enable_buttons()
        self._note_playing = False
        return False

    #####################################################################
    # Close
    #####################################################################
    def _close_request (self, *args):
        GObject.idle_add(self._close)

    #####################################################################
    # Close
    #####################################################################
    def _close (self):
        # self._beep_process is not 0 -> a subprocess was launched at some point
        if self._beep_process is not 0 :
            # If process still alive (or zombie)
            if self._note_playing :
                # Send signal
                try:
                    self._beep_process.send_signal(SIGINT)
                except OSError:
                    print ("Could not SIGINT process")
                # Wait for process to complete
                else:
                    self._beep_process.wait()
        # Close application
        Gtk.main_quit()

    #####################################################################
    # Init
    #####################################################################
    def __init__(self, default_keys=[]):

        self._default_keys = default_keys

        # Variables
        ###########

        # Buttons and handlers
        self._buttons = []

        # Beep process
        self._beep_process = 0

        # Beep queue
        self._beep_queue = deque([])

        # Note playing token
        self._note_playing  = False

        # Keys modified flag
        self._keys_modified = False

        # Settings
        self._beep_length = 1
        self._notestyle = Note.INDEX_FR_NAME
        self._backend = self._SOX_PLUCK

        # Create window
        ###############
        self._window = Gtk.Window()
        self._window.connect("destroy", self._close_request)
        self._window.set_title("Tuner")
        self._window.set_border_width(10)

        # Create vertical box and horizontal sub-boxes
        VBox = Gtk.Box(homogeneous=False, spacing=10, 
                       orientation=Gtk.Orientation.VERTICAL)
        HBox_controls = Gtk.Box()
        #HBox_controls = Gtk.Box(homogeneous=True)
        HBox_keys = Gtk.Box()
        HBox_settings = Gtk.Box(homogeneous=False, spacing=10)

        # Control horizontal box
        ########################

        # Reset keys modifications
        self._reset_button = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        self._reset_button.set_sensitive(False)
        HBox_controls.pack_start(self._reset_button, False, False, 0)
        self._reset_button.connect("clicked", self._reset_keys, HBox_keys)
        self._reset_button.show()

        # Stop playback
        self._stop_playback_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_STOP)
        self._stop_playback_button.set_sensitive(False)
        HBox_controls.pack_end(self._stop_playback_button, False, False, 0)
        self._stop_playback_button.connect("clicked", self._stop_playback_request)
        self._stop_playback_button.show()

        # Play all keys
        self._play_all_button = Gtk.Button(stock=Gtk.STOCK_MEDIA_PLAY)
        HBox_controls.pack_end(self._play_all_button, False, False, 0)
        self._play_all_button.connect("clicked", self._play_all)
        self._play_all_button.show()

        # Keys horizontal box
        #####################

        # Add global incrementor / decrementor buttons
        VBox_inc_dec = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.DOWN, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label=u"\u266D")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_down = Gtk.Button()
        self._button_down.add(HBox_arrow)
        self._button_down.set_size_request(40, -1)
        VBox_inc_dec.pack_end(self._button_down, False, True, 0)
        HBox_arrow.show()
        self._button_down.show()

        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.UP, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label=u"\u266F")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_up = Gtk.Button()
        self._button_up.add(HBox_arrow)
        self._button_up.set_size_request(40, -1)
        VBox_inc_dec.pack_end(self._button_up, False, True, 0)
        HBox_arrow.show()
        self._button_up.show()
        
        VBox_inc_dec.show()
        HBox_keys.pack_start(VBox_inc_dec, True, True, 0)

        self._button_up.connect("clicked", self._tune_up)
        self._button_down.connect("clicked", self._tune_down)

        # Add / remove key buttons
        VBox_add_rem = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.DOWN, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label="-")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_rem = Gtk.Button()
        self._button_rem.add(HBox_arrow)
        self._button_rem.set_size_request(40, -1)
        VBox_add_rem.pack_end(self._button_rem, False, True, 0)
        HBox_arrow.show()
        self._button_rem.show()

        HBox_arrow = Gtk.Box()
        arrow = Gtk.Arrow(arrow_type=Gtk.ArrowType.UP, shadow_type=Gtk.ShadowType.OUT)
        HBox_arrow.pack_start(arrow, True, True, 0)
        arrow.show()
        label = Gtk.Label(label="+")
        HBox_arrow.pack_start(label, True, True, 0)
        label.show()
        self._button_add = Gtk.Button()
        self._button_add.add(HBox_arrow)
        self._button_add.set_size_request(40, -1)
        VBox_add_rem.pack_end(self._button_add, False, True, 0)
        HBox_arrow.show()
        self._button_add.show()

        VBox_add_rem.show()
        HBox_keys.pack_end(VBox_add_rem, True, True, 0)

        self._button_add.connect("clicked", self._add_key, HBox_keys)
        self._button_rem.connect("clicked", self._rem_key)

        # Set default keys
        self._reset_keys(None, HBox_keys)
 
        # Settings horizontal box
        #########################

        # Note style selector
        VBox_notestyle = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label="Notation")
        label.set_alignment(0,1)
        VBox_notestyle.pack_start(label, False, True, 0)
        label.show()
        button = Gtk.RadioButton.new_with_label_from_widget(None, "Française")
        button.connect("clicked", self._set_notestyle, Note.INDEX_FR_NAME)
        VBox_notestyle.pack_start(button, False, True, 0)
        button.show()
        button = Gtk.RadioButton.new_with_label_from_widget(button, "Anglaise")
        button.connect("clicked", self._set_notestyle, Note.INDEX_EN_NAME)
        VBox_notestyle.pack_start(button, False, True, 0)
        button.show()
        HBox_settings.pack_start(VBox_notestyle, False, True, 0)
        VBox_notestyle.show()

        # Separator
        separator = Gtk.VSeparator()
        HBox_settings.pack_start(separator, False, True, 0)
        separator.show()

        # Beep length
        VBox_beep_length= Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label="Durée (s)")
        label.set_alignment(0,1)
        VBox_beep_length.pack_start(label, False, True, 0)
        label.show()
        beep_length_adj = Gtk.Adjustment(value=self._beep_length, \
                                         lower=1, \
                                         upper=10, \
                                         step_increment=1, \
                                         page_increment=1, \
                                         page_size=0)
        beep_length_spin = Gtk.SpinButton(adjustment=beep_length_adj, climb_rate=0, digits=1)
        beep_length_adj.connect("value_changed", self._set_beep_length, beep_length_spin)
        VBox_beep_length.pack_start(beep_length_spin, False, True, 0)
        beep_length_spin.show()
        HBox_settings.pack_start(VBox_beep_length, False, True, 0)
        VBox_beep_length.show()

        # Separator
        separator = Gtk.VSeparator()
        HBox_settings.pack_start(separator, False, True, 0)
        separator.show()

        # Note style selector
        VBox_backend = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label(label="Sortie")
        label.set_alignment(0,1)
        VBox_backend.pack_start(label, False, True, 0)
        label.show()
        button = Gtk.RadioButton.new_with_label_from_widget(None, "sox pluck")
        button.connect("clicked", self._set_backend, self._SOX_PLUCK)
        VBox_backend.pack_start(button, False, True, 0)
        button.show()
        button = Gtk.RadioButton.new_with_label_from_widget(button, "sox sine")
        button.connect("clicked", self._set_backend, self._SOX_SINE)
        VBox_backend.pack_start(button, False, True, 0)
        button.show()
        button = Gtk.RadioButton.new_with_label_from_widget(button, "beep")
        button.connect("clicked", self._set_backend, self._BEEP)
        VBox_backend.pack_start(button, False, True, 0)
        button.show()
        HBox_settings.pack_start(VBox_backend, False, True, 0)
        VBox_backend.show()

        # Show everything
        #################
        VBox.pack_start(HBox_controls, True, True, 0)
        VBox.pack_start(HBox_keys, True, True, 0)
        VBox.pack_start(HBox_settings, True, True, 0)
        HBox_controls.show()
        HBox_keys.show()
        HBox_settings.show()
        VBox.show()
        self._window.add(VBox)
        self._window.show()

        # Poll note queue
        GObject.idle_add(self._play_note_from_queue)

#########################################################################
# main
#########################################################################
def main():
    Gtk.main()
    return 0       

if __name__ == "__main__":
    # Create tuner with default guitar tuning (E, A, D, G, B, e)
    Tuner([16, 21, 26, 31, 35, 40])
    main()

