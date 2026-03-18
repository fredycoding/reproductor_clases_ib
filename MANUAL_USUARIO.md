# Manual de Usuario - Reproductor Seguro de Audio (CustomTkinter)

Este manual esta pensado para personas sin conocimientos tecnicos.

## 1) Para que sirve

La aplicacion permite:

- Abrir y reproducir archivos protegidos `.audx`.
- Preparar una biblioteca protegida a partir de archivos `.mp3` (solo en modo administrador).

## 2) Instalacion rapida (usuario final)

1. Recibe una carpeta llamada `Reproductor`.
2. Copia esa carpeta completa a tu disco local, por ejemplo: `C:\Reproductor`.
3. Abre `Reproductor.exe` con doble clic.

Importante:

- No ejecutes la app desde archivo `.zip` sin extraer.
- No ejecutes desde red/servidor compartido.

## 3) Pantalla principal

La app tiene 2 zonas:

- Zona de usuario: para abrir y reproducir archivos `.audx`.
- Zona de administrador: para convertir `.mp3` en `.audx`.

Tambien puedes cambiar idioma entre `ES` y `EN`.

## 4) Uso normal (reproducir archivos `.audx`)

1. Entra a **Zona de usuario**.
2. Clic en **Abrir audio AUDX**.
3. Selecciona un archivo `.audx`.
4. Escribe la **clave de reproduccion**.
5. Clic en **Cargar audio**.
6. Selecciona la pista y usa los controles de reproduccion.

Controles disponibles:

- Play/Pausa
- Detener
- Anterior / Siguiente
- Barra de avance
- Volumen

## 5) Uso administrador (crear `.audx` desde `.mp3`)

1. Clic en **Ingresar al admin**.
2. Escribe el codigo de administrador y desbloquea.
3. Clic en **Seleccionar MP3**.
4. Clic en **Examinar** para elegir carpeta de salida.
5. Escribe la **clave de acceso**.
6. Clic en **Preparar biblioteca**.

Resultado:

- Se crean archivos `.audx` en la carpeta elegida.

## 6) Atajos de teclado

- `Espacio`: Play/Pausa
- `Izquierda / Derecha`: mover 5 segundos
- `Arriba / Abajo`: volumen
- `N`: siguiente pista
- `P`: pista anterior

## 7) Mensajes comunes y solucion

### "Windows protegió su PC" (SmartScreen)

Puede aparecer en ejecutables nuevos.

- Clic en **Mas informacion**.
- Luego **Ejecutar de todas formas** (si el archivo viene de una fuente confiable).

### No carga el audio

- Verifica que seleccionaste archivo `.audx` valido.
- Verifica que la clave de reproduccion sea correcta.

### No suena el audio

- Revisa volumen de Windows y de la app.
- Verifica que VLC este instalado.
- Cierra otros programas de audio y vuelve a intentar.

## 8) Recomendaciones de uso

- Guarda respaldo de tus archivos `.audx`.
- No compartas la clave por canales inseguros.
- Si cambias la clave, vuelve a preparar la biblioteca.

## 9) Soporte

Si tienes un error, reporta:

- Captura de pantalla del mensaje.
- Paso exacto donde fallo.
- Nombre del archivo usado (`.audx` o `.mp3`).
- Version de Windows.

