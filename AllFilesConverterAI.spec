# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('app', 'app'), ('assets', 'assets'), ('diagrams', 'diagrams'), ('models', 'models'), ('ffmpeg', 'ffmpeg')]
binaries = []
hiddenimports = ['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'PySide6.QtNetwork', 'PySide6.QtXml', 'importlib.metadata', 'importlib_metadata', 'imageio', 'imageio_ffmpeg', 'moviepy', 'moviepy.video.VideoClip', 'moviepy.audio.AudioClip', 'pydub', 'PIL', 'PIL._imaging', 'numpy', 'numpy._core._methods', 'numpy.lib.format', 'cv2', 'speech_recognition', 'pyttsx3', 'psutil', 'docx', 'reportlab', 'PyPDF2', 'unicodedata', 'openpyxl', 'pandas', 'sounddevice', 'easyocr', 'pytesseract', 'paddleocr', 'paddle', 'paddlepaddle', 'pikepdf', 'pymupdf', 'fitz', 'pptx', 'odf', 'pypandoc', 'transformers', 'torch', 'torch.amp', 'torch._C', 'torch._utils', 'torch.functional', 'torch.nn', 'torch.nn.functional', 'torch.optim', 'torch.cuda', 'torch.backends', 'torch.utils', 'torch.utils.data', 'torch.utils.data.dataloader', 'torch.utils.data.dataset', 'torch.utils.data.sampler', 'torchvision', 'torchvision.models']
datas += collect_data_files('transformers')
datas += copy_metadata('imageio')
datas += copy_metadata('imageio-ffmpeg')
datas += copy_metadata('moviepy')
datas += copy_metadata('pydub')
datas += copy_metadata('Pillow')
datas += copy_metadata('numpy')
datas += copy_metadata('opencv-python')
datas += copy_metadata('transformers')
datas += copy_metadata('torch')
datas += copy_metadata('scikit-image')
datas += copy_metadata('pandas')
hiddenimports += collect_submodules('transformers.models.gpt2')
hiddenimports += collect_submodules('transformers.models.dialogpt')
hiddenimports += collect_submodules('transformers.models.conv_ai')
tmp_ret = collect_all('easyocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytesseract')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('paddleocr')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('transformers')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('torch')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('app')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/pre_import_unicodedata.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AllFilesConverterAI',
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
    icon=['assets/icons/app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AllFilesConverterAI',
)
