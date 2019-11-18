# -*- mode: python -*-

block_cipher = None

added_files = [
         ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\log\\*', 'log' ),
         ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\resources\\*', 'resources' ),
         ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\db\\*', 'db' ),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\java\\*', 'java' ),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\i18n\\*', 'i18n' ),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\help\\*', 'help' ),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\config\\*', 'config'),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\temp\\*', 'temp'),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\scripts\\*', 'scripts'),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\dialogs\\*.ui', 'dialogs'),
		 ( 'D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted\\*', '.'),
		
         ]
		 
a = Analysis(['MainWindowLauncher.py'],
             pathex=['D:\\Desarrollo\\workspace\\DMMPlanHeatRetrofitted'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='MainWindowLauncher',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='MainWindowLauncher')
