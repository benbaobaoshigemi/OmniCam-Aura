package local.omnicam.aura;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.IXposedHookZygoteInit;
import de.robv.android.xposed.callbacks.XC_LoadPackage;
import local.jiege.hook.common.Symbols;
import local.jiege.hook.filters.FilterGroupInjector;
import local.jiege.hook.masterfilter.MasterPresetListSync;
import local.jiege.hook.gr.GrPort;
import local.jiege.hook.highpixel.HighPixelEffects;
import local.jiege.hook.pop.PopPort;
import local.jiege.hook.seamless.SeamlessBlurGuard;
import local.jiege.hook.tilt.TiltShiftCapture;
import local.jiege.hook.x10.X10FilterPort;

public final class ModuleEntry implements IXposedHookLoadPackage, IXposedHookZygoteInit {
    @Override public void initZygote(StartupParam param) { Symbols.setModulePath(param.modulePath); }
    @Override public void handleLoadPackage(XC_LoadPackage.LoadPackageParam param) {
        ClassLoader loader = param.classLoader;
        if ("com.coloros.gallery3d".equals(param.packageName)) {
            Symbols.install("gallery", loader, param.appInfo.sourceDir, param.appInfo.dataDir);
            GrPort.installGallery(loader);
        } else if ("com.oplus.camera".equals(param.packageName)) {
            System.loadLibrary("aura_native");
            Symbols.install("camera", loader, param.appInfo.sourceDir, param.appInfo.dataDir);
            PopPort.installCamera(loader, "com.oplus.camera".equals(param.processName));
            FilterGroupInjector.installCamera(loader);
            MasterPresetListSync.install(loader);
            X10FilterPort.installCamera(loader);
            HighPixelEffects.installCamera(loader);
            TiltShiftCapture.installCamera(loader);
            SeamlessBlurGuard.installCamera(loader);
            GrPort.installCamera(loader);
        }
    }
}
