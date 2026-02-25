# Audio Leveler Pro 🎧

Una aplicación de escritorio moderna y eficiente para nivelar el volumen de archivos de audio en Linux.

### ✨ Características principales
* **Interfaz Moderna**: Construida con **GTK4** y **Libadwaita** para una integración perfecta con escritorios Linux actuales.
* **Procesamiento Inteligente**: Utiliza el filtro `loudnorm` de **FFmpeg** para un nivelado de audio profesional.
* **Multitarea**: Procesa múltiples archivos en segundo plano sin bloquear la interfaz.
* **Vista Previa**: Escucha los primeros 10 segundos del audio nivelado antes de procesar todo el archivo.
* **Notificaciones**: Te avisa automáticamente cuando el trabajo ha terminado.

### 🛠️ Requisitos del sistema
[cite_start]El paquete `.deb` instalará automáticamente estas dependencias[cite: 1]:
* `python3`
* `ffmpeg`
* `gir1.2-gtk-4.0`
* `gir1.2-adw-1`

### 🚀 Instalación
1. Ve a la sección de **Releases** de este repositorio.
2. Descarga el archivo `audio-leveler-pro.deb`.
3. Instálalo con:
   ```bash
   sudo dpkg -i audio-leveler-pro.deb
