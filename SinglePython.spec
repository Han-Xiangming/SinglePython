# -*- mode: python ; coding: utf-8 -*-
ver = '0.90'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('interpreter.py', '.'),
        ('magic_commands.py', '.'),
        ('shell.py', '.'),
        ('utils.py', '.'),
        ('config.py', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure,a.zipped_data,
            cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SinglePython' + "-" + ver + "-" + "Windows",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Icon.ico'
)
