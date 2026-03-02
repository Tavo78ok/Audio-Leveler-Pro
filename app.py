#!/usr/bin/env python3
import sys
import os
import threading
import subprocess
import re
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, GLib, Adw

class AudioFile:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.icon_widget = None
        self.label_widget = None
        self.has_clipping = False

class AudioLevelerApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.tavo.audiolvl',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        window = AudioLevelerWindow(application=self)
        window.present()

class AudioLevelerWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Audio Leveler Pro v1.1.4")
        self.set_default_size(750, 650)

        self.files_data = []
        self.is_running = False
        self.current_process = None # Para poder detenerlo

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        # --- BOTONES HEADER ---
        self.btn_add = Gtk.Button(icon_name="list-add-symbolic")
        self.btn_add.set_tooltip_text("Añadir Archivos")
        self.btn_add.connect("clicked", self.on_file_open)
        header.pack_start(self.btn_add)

        self.btn_analyze = Gtk.Button(icon_name="system-search-symbolic")
        self.btn_analyze.set_tooltip_text("Analizar Clipping y dB")
        self.btn_analyze.connect("clicked", self.start_analysis)
        header.pack_start(self.btn_analyze)

        self.btn_clear = Gtk.Button(icon_name="edit-clear-all-symbolic")
        self.btn_clear.set_tooltip_text("Limpiar Lista")
        self.btn_clear.connect("clicked", self.clear_list)
        header.pack_start(self.btn_clear)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.set_margin_top(20); content_box.set_margin_bottom(20)
        content_box.set_margin_start(20); content_box.set_margin_end(20)
        main_box.append(content_box)

        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_min_content_height(300)
        scrolled.set_child(self.list_box)
        content_box.append(scrolled)

        # --- CONFIGURACIÓN ---
        config_frame = Gtk.Frame(label="Ajustes (Target 94dB recomendado)")
        config_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        config_box.set_margin_top(12); config_box.set_margin_bottom(12)
        config_box.set_margin_start(12); config_box.set_margin_end(12)

        self.db_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(value=94, lower=80, upper=100, step_increment=1))
        config_box.append(Gtk.Label(label="Objetivo (dB):"))
        config_box.append(self.db_spin)
        config_frame.set_child(config_box)
        content_box.append(config_frame)

        # --- BOTONES DE ACCIÓN ---
        action_box = Gtk.Box(spacing=10)
        self.btn_start = Gtk.Button(label="Iniciar Nivelado Lossless", hexpand=True)
        self.btn_start.add_css_class("suggested-action")
        self.btn_start.connect("clicked", self.start_processing)

        self.btn_stop = Gtk.Button(label="Detener", sensitive=False)
        self.btn_stop.add_css_class("destructive-action")
        self.btn_stop.connect("clicked", self.stop_all)

        action_box.append(self.btn_start)
        action_box.append(self.btn_stop)
        content_box.append(action_box)

        self.progress_bar = Gtk.ProgressBar(show_text=True)
        content_box.append(self.progress_bar)

    def start_analysis(self, btn):
        if not self.files_data: return
        self.toggle_ui(False)
        self.progress_bar.set_text("Buscando saturación (Clipping)...")
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        self.is_running = True
        for i, audio in enumerate(self.files_data):
            if not self.is_running: break

            # Comando mp3gain -s s para ver volumen y clipping
            cmd = ['mp3gain', '-s', 's', audio.path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout

            # Buscamos volumen y si hay una 'Y' en la columna de clipping
            vol_match = re.search(r'(\d+\.\d+)', output)
            clip_match = "Y" in output or "Yes" in output

            vol_val = vol_match.group(1) if vol_match else "???"
            audio.has_clipping = clip_match

            GLib.idle_add(self.update_analysis_ui, audio, vol_val, (i+1)/len(self.files_data))

        self.is_running = False
        GLib.idle_add(self.toggle_ui, True)

    def update_analysis_ui(self, audio, vol, progress):
        status = f"Actual: {vol} dB"
        if audio.has_clipping:
            status += " ⚠️ (SATURADO)"
            audio.label_widget.add_css_class("error") # Requiere que tu CSS tenga .error { color: red; }
            audio.icon_widget.set_from_icon_name("dialog-warning-symbolic")

        audio.label_widget.set_text(f"{audio.filename}  |  {status}")
        self.progress_bar.set_fraction(progress)

    def start_processing(self, btn):
        if not self.files_data: return
        self.toggle_ui(False)
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        self.is_running = True
        target_db = self.db_spin.get_value()
        for i, audio in enumerate(self.files_data):
            if not self.is_running: break

            diff = target_db - 89.0
            cmd = ['mp3gain', '-r', '-k', '-p', '-d', str(diff), audio.path]
            self.current_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL)
            self.current_process.wait()

            GLib.idle_add(self.update_step, audio, (i+1)/len(self.files_data), i+1)

        self.is_running = False
        GLib.idle_add(self.finish_processing)

    def on_file_open(self, btn):
        d = Gtk.FileDialog.new()
        d.open_multiple(self, None, self.on_file_dialog_response)

    def on_file_dialog_response(self, dialog, result):
        try:
            files = dialog.open_multiple_finish(result)
            for i in range(files.get_n_items()):
                path = files.get_item(i).get_path()
                if not path.lower().endswith('.mp3'): continue
                audio_obj = AudioFile(path)
                self.files_data.append(audio_obj)

                row = Gtk.Box(spacing=10)
                row.set_margin_top(10); row.set_margin_bottom(10)
                row.set_margin_start(10); row.set_margin_end(10)

                icon = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
                label = Gtk.Label(label=audio_obj.filename, xalign=0, hexpand=True)
                row.append(icon); row.append(label)

                audio_obj.icon_widget = icon
                audio_obj.label_widget = label
                self.list_box.append(row)
        except: pass

    def stop_all(self, btn):
        self.is_running = False
        if self.current_process:
            self.current_process.terminate()
        self.progress_bar.set_text("Proceso detenido por el usuario")
        self.toggle_ui(True)

    def toggle_ui(self, s):
        self.btn_start.set_sensitive(s)
        self.btn_add.set_sensitive(s)
        self.btn_analyze.set_sensitive(s)
        self.btn_clear.set_sensitive(s)
        self.btn_stop.set_sensitive(not s)

    def update_step(self, audio, progress, count):
        audio.label_widget.set_text(f"{audio.filename} ✅")
        audio.icon_widget.set_from_icon_name("emblem-ok-symbolic")
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_text(f"Nivelado {count}/{len(self.files_data)}")

    def clear_list(self, btn):
        while child := self.list_box.get_first_child(): self.list_box.remove(child)
        self.files_data = []
        self.progress_bar.set_fraction(0)
        self.progress_bar.set_text("")

    def finish_processing(self):
        self.toggle_ui(True)
        if self.is_running == False: return
        dialog = Adw.MessageDialog(transient_for=self, heading="¡Éxito!", body="Colección nivelada correctamente.")
        dialog.add_response("ok", "De una")
        dialog.present()

if __name__ == "__main__":
    app = AudioLevelerApp(); app.run(sys.argv)

