$exclude = @("venv", "botSalesforce.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "botSalesforce.zip" -Force