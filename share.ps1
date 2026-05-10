Clear-Host

# Get-ChildItem "src\streaming\admin" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

# Get-ChildItem "src\streaming\data_engineering" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

# Get-ChildItem "src\streaming\data_validation" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

# Get-ChildItem "src\streaming\storage" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

# Get-ChildItem "src\streaming\visualizations" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

# Get-ChildItem "tests" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }

Get-ChildItem "docs" -Recurse -File | ForEach-Object { Write-Host "`n=== $($_.FullName) ===`n"; Get-Content $_.FullName }
