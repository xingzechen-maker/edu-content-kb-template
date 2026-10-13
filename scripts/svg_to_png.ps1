# svg_to_png.ps1 —— 用 Edge/Chrome 无头模式把 SVG 渲染为 PNG
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File svg_to_png.ps1 `
#     -SvgPath  "D:\path\chart.svg" `
#     -PngPath  "D:\path\chart.png" `
#     -Width 640 -Height 480
#
# 说明:
#   公众号等平台不支持 SVG，发布前需要转成 PNG。
#   脚本依次尝试 Edge、Chrome；路径找不到时可用 -BrowserPath 指定。
param(
    [Parameter(Mandatory = $true)][string]$SvgPath,
    [Parameter(Mandatory = $true)][string]$PngPath,
    [int]$Width = 640,
    [int]$Height = 480,
    [string]$BrowserPath = ""
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $SvgPath)) { throw "SVG 不存在: $SvgPath" }

if (-not $BrowserPath) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )
    $BrowserPath = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $BrowserPath) { throw "未找到 Edge/Chrome，请用 -BrowserPath 指定浏览器路径" }
}

$uri = ([System.Uri](Resolve-Path $SvgPath)).AbsoluteUri
& $BrowserPath --headless --disable-gpu --force-device-scale-factor=2 `
    --screenshot="$PngPath" --window-size=$Width,$Height $uri | Out-Null

if (Test-Path $PngPath) {
    $size = [math]::Round((Get-Item $PngPath).Length / 1KB, 1)
    Write-Output "[OK] $PngPath ($size KB)"
} else {
    throw "渲染失败，未生成 PNG"
}
