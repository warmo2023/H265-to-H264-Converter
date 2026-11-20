$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ffmpeg = Join-Path $root 'ffmpeg.exe'
if (-not (Test-Path $ffmpeg)) { throw '缺少 ffmpeg.exe。请先运行 setup.ps1 下载运行引擎。' }
pyinstaller --noconfirm --clean --onefile --windowed --name '江西农网视频兼容性转换工具' --icon (Join-Path $root 'app_icon.ico') --add-binary "$ffmpeg;." --add-data "$(Join-Path $root 'app_icon.ico');." (Join-Path $root 'h265_to_h264.py')
Write-Host "完成：$root\dist\江西农网视频兼容性转换工具.exe"
