$ErrorActionPreference = "Stop"
# Use current directory
$WorkingDir = Get-Location

# 1. Combine Markdown files
$combinedFile = "combined.md"
Clear-Content $combinedFile -ErrorAction SilentlyContinue

$files = Get-ChildItem "*.md" | Where-Object { $_.Name -match "^\d{2}-" } | Sort-Object Name
$first = $true
foreach ($file in $files) {
    if (-not $first) {
        Add-Content $combinedFile "`n`n```{=latex}`n\newpage`n````n`n" -Encoding UTF8
    }
    Get-Content $file.FullName -Encoding UTF8 | Add-Content $combinedFile -Encoding UTF8
    $first = $false
}

# 2. Create CSS
$cssContent = @"
body { font-family: "Microsoft YaHei", sans-serif; }
h1, h2, h3 { font-family: "Microsoft YaHei", sans-serif; }
code { font-family: Consolas, monospace; }
h1 { page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
@page { size: A4; margin: 20mm 18mm; }
pre { white-space: pre-wrap; }
math[display="block"] { text-align: center; }
"@
Set-Content "book.css" $cssContent -Encoding UTF8

# 3. Generate HTML with Pandoc
Write-Host "Running pandoc..."
pandoc $combinedFile -f markdown -t html5 -s --mathml -c book.css --metadata pagetitle="ModernCryptographyMadeEasy" -o book.html

# 4. Convert HTML to PDF with Edge (Chromium)
Write-Host "Converting HTML to PDF with Edge..."
$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edgePath)) {
    $edgePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
}

$htmlPath = "file:///" + (Resolve-Path "book.html").Path.Replace("\", "/")
$pdfPath = (Resolve-Path ".").Path + "\ModernCryptographyMadeEasy.pdf"

& $edgePath --headless=new --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw --virtual-time-budget=15000 --print-to-pdf="$pdfPath" "$htmlPath"

Write-Host "Build complete! PDF saved to $pdfPath"
