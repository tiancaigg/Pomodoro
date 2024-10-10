# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/hudonghui/Codes/pomodoro_mac/src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/hudonghui/Codes/pomodoro_mac/src', 'src')],
    hiddenimports=['PyQt6', 'yaml', 'playsound'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pomodoro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/hudonghui/Codes/pomodoro_mac/pomodoro.png'],
)
app = BUNDLE(
    exe,
    name='Pomodoro.app',
    icon='/Users/hudonghui/Codes/pomodoro_mac/pomodoro.png',
    bundle_identifier='com.yourcompany.pomodoro',
)
