# -*- mode: python -*-
#~ a = Analysis(['delete_old_files.py', 'delete_old_files.py', 'PYMODULE'],
a = Analysis(['delete_old_files.py'],
             #~ pathex=['V:\\workspace\\python-code-snippets\\ftp-tools'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\delete_old_files', 'delete_old_files.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries + [("README.creole","README.creole","DATA")],
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name="dist")