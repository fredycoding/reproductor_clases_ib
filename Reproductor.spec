# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('secure_audio_app\\frontend\\index.html', 'secure_audio_app\\frontend'),
        ('secure_audio_app\\frontend\\styles.css', 'secure_audio_app\\frontend'),
        ('secure_audio_app\\frontend\\app.js', 'secure_audio_app\\frontend'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.qt',
        'qtpy',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pythonnet',
        'clr_loader',
        'clr',
        'webview.platforms.edgechromium',
        'webview.platforms.winforms',
        'PyQt5',
        'PyQt6',
        'PyQtWebEngine',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Reproductor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Reproductor',
)
