$url = "https://p16-cc-image-search-sign-sg.ibyteimg.com/tos-alisg-i-h9hire4aei-sg/4084961164f34d7dadc9605166d2084b~tplv-h9hire4aei-image.jpeg?rk3s=add9cc80&x-expires=1786509813&x-signature=5G0vlzLmpu9NPp21Ndal1MgrsE8%3D"
$outFile = "h:\DEV\MyProjects\BidGenerator\.trae\skills\ian-xiaohei-illustrations\assets\ai-market-research-pricing-illustrations\01-pain-points.jpg"
$response = Invoke-WebRequest -Uri $url -TimeoutSec 30 -UseBasicParsing
[System.IO.File]::WriteAllBytes($outFile, $response.Content)
$size = (Get-Item $outFile).Length
$bytes = [System.IO.File]::ReadAllBytes($outFile)
$hex = ($bytes[0..7] | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
Write-Output "OK: $size bytes | Header: $hex"
