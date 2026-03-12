Write-Host "-------------------------------------"
Write-Host " Mermaid Diagram Renderer"
Write-Host "-------------------------------------"

# Check mermaid-cli availability
$mmdc = (Get-Command mmdc -ErrorAction SilentlyContinue)

if (-not $mmdc) {
    Write-Error "Mermaid CLI not found. Install using: npm install -g @mermaid-js/mermaid-cli"
    exit 1
}

$docsPath = Join-Path $PSScriptRoot "."
$renderOut = Join-Path $docsPath "rendered"

if (-not (Test-Path $renderOut)) {
    New-Item -ItemType Directory -Path $renderOut | Out-Null
}

$files = Get-ChildItem -Path $docsPath -Filter *.mmd

if ($files.Count -eq 0) {
    Write-Warning "No .mmd files found in docs folder."
    exit 0
}

foreach ($file in $files) {
    $name = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)

    $svgOut = Join-Path $renderOut "$name.svg"
    $pngOut = Join-Path $renderOut "$name.png"

    Write-Host "Rendering $($file.Name)..."

    mmdc -i $file.FullName -o $svgOut
    mmdc -i $file.FullName -o $pngOut

    Write-Host " Created -> $svgOut"
    Write-Host " Created -> $pngOut"
}

Write-Host "-------------------------------------"
Write-Host " Done! Rendered files are in:"
Write-Host " $renderOut"
Write-Host "-------------------------------------"
