# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/saas_bench/agents/bash_agent/run_test.py'],
    pathex=[],
    binaries=[],
    datas=[('src/saas_bench/tool_docs.json', 'saas_bench'), ('src/saas_bench/agents/simulator_instructions.md', 'saas_bench/agents')],
    hiddenimports=['saas_bench'],
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
    name='saas-bench-cli',
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
)
