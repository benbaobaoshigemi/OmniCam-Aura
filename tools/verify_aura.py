from pathlib import Path
from zipfile import ZipFile
import subprocess
import json
import os

PROJECT = Path(__file__).resolve().parent.parent
MODULE = PROJECT / 'module'
APK = MODULE / 'omnicam-aura-1.1.0.apk'
ARCHIVE = PROJECT / 'OmniCam-Aura-1.1.0-KSU.zip'
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
build_tools = sorted((Path(sdk_path) / 'build-tools').glob('*'), reverse=True)
BUILD_TOOLS = next((p for p in build_tools if (p / 'aapt2.exe').exists() and (p / 'apksigner.bat').exists()), None)
if BUILD_TOOLS is None:
    raise RuntimeError('Android SDK build-tools with aapt2 and apksigner are required')

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

with ZipFile(ARCHIVE) as bundle, ZipFile(APK) as apk:
    require(bundle.testzip() is None, 'Module archive CRC failed')
    names = bundle.namelist()
    require([n for n in names if n.endswith('.apk')] == [APK.name], 'Expected exactly one Aura APK')
    require(bundle.read(APK.name) == APK.read_bytes(), 'Packaged APK differs from build')
    require('assets/xposed_init' in apk.namelist(), 'LSPosed Java entry missing')
    require(apk.read('assets/xposed_init').strip() == b'local.omnicam.aura.ModuleEntry', 'Wrong LSPosed entry')
    require(apk.read('assets/native_init').strip() == b'libaura_native.so', 'Wrong native entry')
    require('lib/arm64-v8a/libaura_native.so' in apk.namelist(), 'GR/POP native library missing')
    require(not any(b'local.jiege.camera' in apk.read(n) for n in apk.namelist() if n.endswith('.dex')), 'Old package reference in Aura hooks')
    for removed in ('master_hncs/', 'unlock25mp/', 'audio_policy_volumes.xml'):
        require(not any(n.startswith('payload/' + removed) for n in names), f'Unrelated payload: {removed}')
    require(not any('/meishe_lut/JG_' in n or '/meishe_lut/LUT65_' in n or '/meishe_lut/LeicaM9' in n for n in names), 'Muse LUTs leaked into Aura')
    required = ('libAlgoInterface.so', 'libBasicTonePhoto.so', 'libBasicTonePhotoX9.so', 'libBasicTonePhotoX10.so', 'libmsnativefilter.so')
    require(all('system/odm/lib64/' + n in names for n in required), 'Capture backend missing')
    for name in ('qing_tou.bin', 'hu_po.bin', 'polaroid_sdr.mslut'):
        require('payload/meishe_lut/' + name in names, f'Missing LUT: {name}')

manifest = subprocess.check_output([str(BUILD_TOOLS / 'aapt2.exe'), 'dump', 'xmltree', str(APK), '--file', 'AndroidManifest.xml'], text=True, encoding='utf-8')
badging = subprocess.check_output([str(BUILD_TOOLS / 'aapt2.exe'), 'dump', 'badging', str(APK)], text=True, encoding='utf-8')
require("name='local.omnicam.aura'" in badging and "application-label:'OmniCam Aura'" in badging, 'APK identity mismatch')
resources = subprocess.check_output([str(BUILD_TOOLS / 'aapt2.exe'), 'dump', 'resources', str(APK)], text=True, encoding='utf-8')
for name in ('snap_switch_on', 'snap_switch_off', 'snap_switch_1m', 'snap_switch_2_5m', 'snap_switch_5m'):
    require('drawable/' + name in resources, f'GR snap focus icon was stripped: {name}')
for component in ('E: activity ', 'E: activity-alias ', 'E: provider ', 'E: service ', 'E: receiver '):
    require(component not in manifest, f'Unexpected UI/component: {component}')
scope = (PROJECT / 'app/src/main/res/values/arrays.xml').read_text(encoding='utf-8')
require('com.oplus.camera' in scope and 'com.coloros.gallery3d' in scope and '<item>android</item>' not in scope, 'Scope mismatch')
algo = json.loads((MODULE / 'payload/oplus_camera_algo_switch_config').read_bytes())
for mode in ('common', 'portrait', 'aiHighPixel'):
    group = next(g for g in algo['aps_capture_configs'] if g['mode'] == mode)
    for camera in (0, 1):
        entity = next(e for e in group['entity'] if e['id'] == camera)
        require(entity['aps_algo_color_palette'] == 1, f'Palette capture node missing: {mode}/{camera}')
for script in ('post-fs-data.sh', 'service.sh'):
    text = (MODULE / script).read_text(encoding='utf-8')
    for removed in ('master_hncs', 'unlock25mp', 'audio_policy_volumes'):
        require(removed not in text, f'Unrelated mount/staging: {removed}')
subprocess.run(['cmd', '/c', str(BUILD_TOOLS / 'apksigner.bat'), 'verify', str(APK)], check=True)
print('PASS: signed headless Aura APK; camera/gallery scope; GR/POP backends and all six palette capture nodes present; Muse-only payloads removed')
