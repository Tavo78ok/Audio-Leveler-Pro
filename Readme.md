##🔊 Audio Leveler Pro v1.1.4 

Audio Leveler Pro es una herramienta de nivelación de audio de alta precisión diseñada para entornos Linux (GTK4/Libadwaita). A diferencia de otros normalizadores, esta versión utiliza un motor Lossless, lo que permite ajustar el volumen sin recodificar el archivo, manteniendo el bitrate original (ej. 256kbps) y el "vibrante" del sonido intacto.

🚀 Características Principales:

💎 Nivelación Lossless: Ajuste de ganancia mediante metadatos sin tocar la cadena de bits de audio.
⚡ Velocidad Ultra-Rápida: Procesa archivos y carpetas completas en segundos gracias al motor mp3gain.

🔍 Análisis de Precisión: Muestra el nivel de dB actual de cada pista antes de procesar.

⚠️ Detección de Clipping: Identifica automáticamente si un archivo original ya está saturado (roto).

🛑 Control Total: Botón de parada instantánea para detener procesos largos de forma segura.

🎨 Interfaz ArgOs Platinum: Diseño moderno basado en Libadwaita con soporte nativo para modo oscuro.

🛠️ Instalación:

Para que el "Motor Lossless" funcione, necesitas instalar la dependencia principal en tu sistema:

sudo apt update && sudo apt install -y mp3gain

Luego, simplemente clona este repositorio y corre la aplicación:

python3 audio-leveler-pro.py

📖 Cómo usar:

Añadir: Usa el botón + para cargar tus archivos MP3.
Analizar: Presiona la lupa para ver el volumen actual y detectar si hay clipping.

Configurar: Ajusta el objetivo (Recomendado: 94dB para potencia máxima sin distorsión).
Iniciar: Pulsa "Iniciar Nivelado Lossless" y disfruta de tu música nivelada en segundos.

📝 Changelog v1.1.4

Migración de motor FFMPEG a MP3Gain (Adiós a la pérdida de calidad).
Se eliminó la recodificación forzada a 128kbps; ahora el bitrate original se respeta al 100%.
Implementación de hilos (threading) para que la UI nunca se congele.
Desarrollado por Tavo para el ecosistema ArgOs.

<img width="1440" height="900" alt="Captura de pantalla_2026-03-02_01-51-24" src="https://github.com/user-attachments/assets/a2382a61-f3ce-4e73-8daa-fbb4a88486a6" />



<img width="1440" height="900" alt="Captura de pantalla_2026-03-02_01-51-48" src="https://github.com/user-attachments/assets/ddfa4e51-423e-404e-84cc-a5b14f98ab63" />

⚖️ Licencia
Este proyecto es Software Libre bajo la licencia GNU GPLv3.

