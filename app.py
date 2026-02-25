#!/usr/bin/env python3
import sys
import os
import threading
import subprocess
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, GLib, Adw

class AudioFile:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.icon_widget = None

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
        self.set_title("Audio Leveler Pro")
        self.set_default_size(700, 600)

        self.files_data = []
        self.is_running = False
        self.process = None

        # --- Estructura Principal ---
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        # Definición de márgenes explícita
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        main_box.append(content_box)

        # Botones de Archivo
        file_btns_box = Gtk.Box(spacing=10)
        file_btns_box.set_halign(Gtk.Align.CENTER)

        self.btn_add = Gtk.Button(label="Añadir Archivos")
        self.btn_add.set_icon_name("list-add-symbolic")
        self.btn_add.connect("clicked", self.on_file_open)

        self.btn_clear = Gtk.Button(label="Limpiar Lista")
        self.btn_clear.set_icon_name("edit-clear-all-symbolic")
        self.btn_clear.connect("clicked", self.clear_list)

        file_btns_box.append(self.btn_add)
        file_btns_box.append(self.btn_clear)
        content_box.append(file_btns_box)

        # Lista
        self.list_box = Gtk.ListBox()
        self.list_box.add_css_class("boxed-list")
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_min_content_height(250)
        scrolled.set_child(self.list_box)
        content_box.append(scrolled)

        # Configuración
        config_frame = Gtk.Frame(label="Ajustes de Nivelado")

        # Corregido: Gtk.Box sin argumentos de margen en el constructor
        config_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        config_box.set_margin_top(12)
        config_box.set_margin_bottom(12)
        config_box.set_margin_start(12)
        config_box.set_margin_end(12)

        self.db_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(value=-14, lower=-30, upper=-5, step_increment=1))
        self.btn_preview = Gtk.Button(label="Vista Previa (10s)")
        self.btn_preview.set_icon_name("media-playback-start-symbolic")
        self.btn_preview.connect("clicked", self.play_preview)

        config_box.append(Gtk.Label(label="Objetivo (LUFS):"))
        config_box.append(self.db_spin)
        config_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        config_box.append(self.btn_preview)

        config_frame.set_child(config_box)
        content_box.append(config_frame)

        # Controles e Info
        action_box = Gtk.Box(spacing=10)
        self.btn_start = Gtk.Button(label="Iniciar", hexpand=True)
        self.btn_start.add_css_class("suggested-action")
        self.btn_start.connect("clicked", self.start_processing)

        self.btn_stop = Gtk.Button(label="Detener", sensitive=False)
        self.btn_stop.add_css_class("destructive-action")
        self.btn_stop.connect("clicked", self.stop_processing)

        action_box.append(self.btn_start)
        action_box.append(self.btn_stop)
        content_box.append(action_box)

        self.progress_bar = Gtk.ProgressBar(show_text=True)
        content_box.append(self.progress_bar)

    def on_file_open(self, btn):
        dialog = Gtk.FileDialog.new()
        dialog.open_multiple(self, None, self.on_file_dialog_response)

    def on_file_dialog_response(self, dialog, result):
        try:
            files = dialog.open_multiple_finish(result)
            for i in range(files.get_n_items()):
                path = files.get_item(i).get_path()
                audio_obj = AudioFile(path)
                self.files_data.append(audio_obj)

                row = Gtk.Box(spacing=10)
                row.set_margin_top(6)
                row.set_margin_bottom(6)
                row.set_margin_start(10)
                row.set_margin_end(10)

                icon = Gtk.Image.new_from_icon_name("audio-x-generic-symbolic")
                label = Gtk.Label(label=audio_obj.filename, xalign=0, hexpand=True)

                row.append(icon)
                row.append(label)
                audio_obj.icon_widget = icon
                self.list_box.append(row)
        except Exception:
            pass

    def clear_list(self, btn):
        while True:
            child = self.list_box.get_first_child()
            if not child: break
            self.list_box.remove(child)
        self.files_data, self.is_running = [], False
        self.progress_bar.set_fraction(0)
        self.progress_bar.set_text("")

    def play_preview(self, btn):
        if not self.files_data: return
        cmd = ['ffplay', '-nodisp', '-autoexit', '-t', '10', '-i', self.files_data[0].path,
               '-af', f'loudnorm=I={self.db_spin.get_value()}']
        subprocess.Popen(cmd)

    def start_processing(self, btn):
        if not self.files_data: return
        self.toggle_ui(False)
        threading.Thread(target=self.process_files).start()

    def process_files(self):
        target_db = self.db_spin.get_value()
        base_dir = os.path.dirname(self.files_data[0].path)
        output_dir = os.path.join(base_dir, "Nivelados")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i, audio in enumerate(self.files_data):
            if not self.is_running: break

            out_name = f"Lvl_{audio.filename}"
            if not out_name.lower().endswith(".mp3"):
                out_name = os.path.splitext(out_name)[0] + ".mp3"

            out_path = os.path.join(output_dir, out_name)

            cmd = ['ffmpeg', '-y', '-i', audio.path, '-af', f'loudnorm=I={target_db}',
                   '-c:a', 'libmp3lame', '-q:a', '2', out_path]

            self.process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            self.process.wait()
            GLib.idle_add(self.update_step, audio, (i+1)/len(self.files_data), i+1)

        GLib.idle_add(self.finish_processing, output_dir)

    def update_step(self, audio, progress, count):
        if audio.icon_widget:
            audio.icon_widget.set_from_icon_name("emblem-ok-symbolic")
        self.progress_bar.set_fraction(progress)
        self.progress_bar.set_text(f"Procesado {count}/{len(self.files_data)}")

    def toggle_ui(self, s):
        self.is_running = not s
        self.btn_start.set_sensitive(s)
        self.btn_add.set_sensitive(s)
        self.btn_clear.set_sensitive(s)
        self.btn_preview.set_sensitive(s)
        self.btn_stop.set_sensitive(not s)

    def finish_processing(self, out_path):
        self.toggle_ui(True)
        self.send_notification("Completado", f"Archivos guardados en: {out_path}")

    def stop_processing(self, btn):
        self.is_running = False
        if self.process: self.process.terminate()

    def send_notification(self, title, body):
        notif = Gio.Notification.new(title)
        notif.set_body(body)
        self.get_application().send_notification("audio-lvl", notif)

if __name__ == "__main__":
    app = AudioLevelerApp()
    app.run(sys.argv)


