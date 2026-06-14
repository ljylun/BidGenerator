$base = "h:\DEV\MyProjects\BidGenerator\.trae\skills\ian-xiaohei-illustrations"
$files = @(
    "check-images.ps1", "check-new.ps1", "compare-images.ps1",
    "download-final.ps1", "download-from-file.ps1", "download-immediate.ps1",
    "gen-and-save.ps1", "rename-images.ps1", "save-all.ps1",
    "save-url.ps1", "test-api.ps1", "test-api2.ps1", "test-api3.ps1",
    "test-api4.ps1", "test-api5.ps1", "test-headers.ps1",
    "test-http.jpg", "test-httpclient.ps1", "test-output.jpg",
    "test-output2.jpg", "test-output5.jpg", "test-webfetch.ps1",
    "url-img1.txt", "verify-images.ps1", "prompts"
)
foreach ($f in $files) {
    $path = Join-Path $base $f
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force
        Write-Output "Deleted: $f"
    }
}
# Also delete test jpg in assets
$testJpg = Join-Path $base "assets\ai-market-research-pricing-illustrations\test-output.jpg"
if (Test-Path $testJpg) { Remove-Item $testJpg -Force }
$testJpg2 = Join-Path $base "assets\ai-market-research-pricing-illustrations\test-output2.jpg"
if (Test-Path $testJpg2) { Remove-Item $testJpg2 -Force }
$testJpg5 = Join-Path $base "assets\ai-market-research-pricing-illustrations\test-output5.jpg"
if (Test-Path $testJpg5) { Remove-Item $testJpg5 -Force }
$testHttp = Join-Path $base "assets\ai-market-research-pricing-illustrations\test-http.jpg"
if (Test-Path $testHttp) { Remove-Item $testHttp -Force }
Write-Output "Cleanup done!"
