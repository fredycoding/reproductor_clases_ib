# Manual de Usuario - Reproductor Audio

Este manual explica el uso diario de la aplicacion.

## 1) Para que sirve

La aplicacion permite:

- Reproducir archivos protegidos `.audx` (modo usuario).
- Crear archivos `.audx` desde `.mp3` (modo admin).

## 2) Instalacion para usuario final

1. Recibe la carpeta `Reproductor`.
2. Copia la carpeta completa a disco local, por ejemplo `C:\Reproductor`.
3. Abre `Reproductor.exe`.

Recomendaciones:

- No ejecutar desde `.zip` sin extraer.
- No ejecutar desde red compartida.

## 3) Pantalla principal

La app tiene:

- Zona de usuario
- Zona de administrador
- Selector de idioma `ES/EN`

## 4) Como reproducir un archivo `.audx`

1. Entra a `Zona de usuario`.
2. Clic en `Abrir audio AUDX`.
3. Selecciona el archivo `.audx`.
4. Escribe la clave de reproduccion.
5. Clic en `Cargar audio`.

Importante:

- Si la clave es correcta, el panel de clave se oculta automaticamente.
- Para cargar otro archivo, vuelve a usar `Abrir audio AUDX`; ahi reaparece el panel de clave.

## 5) Controles disponibles

- `Play/Pausa`
- `Detener`
- `Barra de avance`
- `Volumen`

Atajo activo:

- `Espacio`: Play/Pausa

Nota:

- Los botones `Anterior` y `Siguiente` ya no se usan en esta version.

## 6) Como crear archivos `.audx` (admin)

1. Clic en `Ingresar al admin`.
2. Ingresa el codigo de administrador.
3. Clic en `Seleccionar MP3`.
4. Clic en `Examinar` para elegir carpeta de salida.
5. Escribe la clave de acceso.
6. Clic en `Preparar biblioteca`.

Resultado:

- Se generan archivos `.audx` en la carpeta elegida.

## 7) Estado que la app guarda al cerrar

La app recuerda automaticamente:

- idioma
- tamano y posicion de ventana
- modo actual
- volumen
- carpeta de salida del admin

## 8) Problemas comunes

### No carga el audio

- Verifica que el archivo sea `.audx` valido.
- Verifica que la clave de reproduccion sea correcta.

### No se escucha audio

- Revisa volumen del sistema y de la app.
- Verifica instalacion de VLC.

### SmartScreen en Windows

Si aparece `Windows protegió su PC`:

1. Clic en `Mas informacion`.
2. Clic en `Ejecutar de todas formas` (si el archivo es confiable).

## 9) Soporte

Si reportas un error, envia:

- captura del mensaje
- paso exacto donde falla
- tipo de archivo usado (`.audx` o `.mp3`)
- version de Windows
