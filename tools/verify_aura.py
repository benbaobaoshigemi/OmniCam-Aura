from pathlib import Path
from zipfile import ZipFile
import os
import subprocess

PROJECT = Path(__file__).resolve().parent.parent
MODULE = PROJECT / 'module'
VERSION = next(line.partition('=')[2].strip() for line in (MODULE / 'module.prop').read_text(encoding='utf-8').splitlines()
               if line.startswith('version='))
APK = MODULE / f'omnicam-aura-{VERSION}.apk'
ARCHIVE = PROJECT / f'OmniCam-Aura-{VERSION}-KSU.zip'
sdk_path = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
if not sdk_path:
    properties = PROJECT / 'local.properties'
    if properties.exists():
        for line in properties.read_text(encoding='utf-8').splitlines():
            if line.startswith('sdk.dir='):
                sdk_path = line.partition('=')[2].replace('\\:', ':').replace('\\\\', '\\')
                break
if not sdk_path:
    raise RuntimeError('Set ANDROID_HOME or ANDROID_SDK_ROOT, or create local.properties with sdk.dir')
APKSIGNER = next((p / 'apksigner.bat' for p in sorted((Path(sdk_path) / 'build-tools').glob('*'), reverse=True)
                  if (p / 'apksigner.bat').exists()), None)
if APKSIGNER is None:
    raise RuntimeError('Android SDK build-tools with apksigner are required')


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


with ZipFile(ARCHIVE) as bundle, ZipFile(APK) as apk:
    require(bundle.testzip() is None, 'Module archive CRC failed')
    require(bundle.read(APK.name) == APK.read_bytes(), 'Packaged APK differs from build')
    require(apk.read('assets/xposed_init').strip() == b'local.omnicam.aura.ModuleEntry', 'Wrong LSPosed entry')
    require(apk.read('assets/native_init').strip() == b'libaura_native.so', 'Wrong native entry')
subprocess.run(['cmd', '/c', str(APKSIGNER), 'verify', str(APK)], check=True)
print(f'PASS: Aura {VERSION}')
