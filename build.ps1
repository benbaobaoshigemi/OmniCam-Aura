$ErrorActionPreference = 'Stop'
$project = $PSScriptRoot
$python = if ($env:OMNICAM_PYTHON) { $env:OMNICAM_PYTHON } else { (Get-Command python -ErrorAction Stop).Source }
$version = '1.1.1'
$apkName = "omnicam-aura-$version.apk"
$archive = Join-Path $project "OmniCam-Aura-$version-KSU.zip"
$gitBash = Join-Path $env:ProgramFiles 'Git/bin/bash.exe'
if (Test-Path -LiteralPath $gitBash) {
    & $gitBash -n (Join-Path $project 'module/post-fs-data.sh') (Join-Path $project 'module/post-mount.sh') (Join-Path $project 'module/service.sh')
    if ($LASTEXITCODE -ne 0) { throw 'module shell syntax failed' }
}
$drive = (70..90 | ForEach-Object { [char]$_ } | Where-Object { -not (Test-Path "$($_):\") } | Select-Object -Last 1)
if (-not $drive) { throw 'no free drive letter for the build' }
subst "$($drive):" $project
if ($LASTEXITCODE -ne 0) { throw 'drive mapping failed' }
try {
    Push-Location "$($drive):\"
    try {
        & .\gradlew.bat :app:assembleRelease --console=plain
        if ($LASTEXITCODE -ne 0) { throw 'gradle build failed' }
    } finally { Pop-Location }
} finally { subst "$($drive):" /D }
Copy-Item -LiteralPath (Join-Path $project 'app/build/outputs/apk/release/app-release.apk') -Destination (Join-Path $project "module/$apkName")
& $python (Join-Path $project 'tools/zip_module.py') (Join-Path $project 'module') $archive
if ($LASTEXITCODE -ne 0) { throw 'module packaging failed' }
& $python (Join-Path $project 'tools/verify_aura.py')
if ($LASTEXITCODE -ne 0) { throw 'verification failed' }
Get-Item (Join-Path $project "module/$apkName"), $archive | Select-Object FullName, Length
