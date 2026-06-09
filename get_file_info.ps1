$content = Get-Content "h:\DEV\MyProjects\BidGenerator\doc\技术标\04_软件运维方案.md" -Raw -Encoding UTF8
$content.Length | Out-File -FilePath "h:\DEV\MyProjects\BidGenerator\file_length.txt" -Encoding UTF8
($content | Select-String -Pattern "`n" -AllMatches).Matches.Count | Out-File -FilePath "h:\DEV\MyProjects\BidGenerator\file_lines.txt" -Encoding UTF8
