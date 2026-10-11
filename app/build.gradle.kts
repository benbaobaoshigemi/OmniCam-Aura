plugins {
    id("com.android.application")
}

android {
    namespace = "local.omnicam.aura"
    compileSdk = 37
    ndkVersion = "29.0.14206865"

    defaultConfig {
        applicationId = "local.omnicam.aura"
        minSdk = 28
        targetSdk = 35
        versionCode = 4
        versionName = "1.1.1"
        ndk { abiFilters += "arm64-v8a" }
        externalNativeBuild {
            cmake { arguments += listOf("-DANDROID_STL=c++_static") }
        }
    }

    val releaseKeystore = System.getenv("OMNICAM_KEYSTORE")
    signingConfigs {
        if (releaseKeystore != null) {
            create("port") {
                storeFile = file(releaseKeystore)
                storePassword = System.getenv("OMNICAM_STORE_PASSWORD")
                    ?: error("OMNICAM_STORE_PASSWORD is required with OMNICAM_KEYSTORE")
                keyAlias = System.getenv("OMNICAM_KEY_ALIAS")
                    ?: error("OMNICAM_KEY_ALIAS is required with OMNICAM_KEYSTORE")
                keyPassword = System.getenv("OMNICAM_KEY_PASSWORD")
                    ?: error("OMNICAM_KEY_PASSWORD is required with OMNICAM_KEYSTORE")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            signingConfig = signingConfigs.getByName(if (releaseKeystore != null) "port" else "debug")
            vcsInfo.include = false
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
            version = "3.22.1"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures { compose = false }

    packaging {
        // LSPosed loads the native part straight from the APK (assets/native_init).
        jniLibs.useLegacyPackaging = false
    }
}

dependencies {
    compileOnly(files("libs/api-82.jar"))
    implementation("org.luckypray:dexkit:2.3.0")
}
