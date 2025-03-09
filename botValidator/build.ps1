$exclude = @("venv", "botValidator.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botValidator.zip" -Force