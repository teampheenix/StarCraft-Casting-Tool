# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:\\Users\\tasch\\GitHub\\StarCraft-Casting-Tool\\StarCraftCastingTool.py'],
             pathex=['C:\\Users\\tasch\\GitHub\\StarCraft-Casting-Tool',
                     'C:\\Users\\tasch\\GitHub\\StarCraft-Casting-Tool'],
             binaries=[],
             datas=[('src/*', 'src'), ('locales', 'locales'),
                    ('CHANGELOG.md', '.'), ('README.md', '.')],
             hiddenimports=[],
             hookspath=[
                 'c:\\users\\tasch\\appdata\\local\\programs\\python\\python38\\lib\\site-packages\\pyupdater\\hooks', 'hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='win',
          icon='src\\scct.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)
