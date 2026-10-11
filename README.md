# OmniCam Aura

![OmniCam Aura 图标](artwork/OmniCam-Aura.png)

PMA110 相机 7.006.77 的无界面 KernelSU 模块与 LSPosed 插件。

## 功能

- 理光 GR 模式、影调、焦距条、快照对焦及相机／相册水印。
- POP 模式、复古资源与高像素支持；滑杆进成片，成片走 Ultra HDR。
- 移轴拍照模式。
- 专业视频（含 O-Log2）强制启用 ISZ：主摄 2x、长焦 6x 去掉 ISO 门限（模块目录放 `disable_pro_video_isz` 可关闭）。
- Find X10 的清透／琥珀滤镜、调色盘预览与成片、闪光灯亮度、AI 构图配置及哈苏相关滤镜、调色盘和柔光资源。

LSPosed 包名为 `local.omnicam.aura`，作用域为 `com.oplus.camera` 和 `com.coloros.gallery3d`。APK 没有 Activity、启动入口或设置界面，功能固定启用。

## 安装

1. 在 KernelSU 中安装发行页的模块 ZIP。
2. 安装同一发行版的 APK，并在 LSPosed 中启用 Aura，勾选相机和相册作用域。
3. 重启设备使模块挂载和 Hook 生效。

Aura 与 OmniCam Muse 的相机 Hook 和挂载资源重叠，只启用其中一套。除 PMA110／相机 7.006.77 外的设备组合尚未验证。

## 构建

在 Windows 上安装 JDK 17、Android SDK（含 API 37、Build Tools、NDK 29.0.14206865 和 CMake 3.22.1）、Python 3 与 Git，然后运行 `./build.ps1`。脚本会生成配套 APK 和位于项目上级目录的 KernelSU ZIP，并进行结构与签名检查。设置 `ANDROID_HOME`／`ANDROID_SDK_ROOT` 或通过 `local.properties` 指向 SDK。

构建默认使用 Android 调试签名。若要使用自己的发布证书，设置 `OMNICAM_KEYSTORE`、`OMNICAM_STORE_PASSWORD`、`OMNICAM_KEY_ALIAS` 和 `OMNICAM_KEY_PASSWORD`；证书与密码均不应提交到仓库。不同证书签发的 APK 不能直接覆盖安装。

## 来源与许可

本仓库的原创源码和脚本按 [MIT 许可证](LICENSE) 开放。相机厂商的库、固件配置及媒体资源保留原权利人的权利；MIT 许可证不授予这些文件的再许可。项目与相机厂商无隶属关系。
