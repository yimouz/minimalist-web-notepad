$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\MinitexNotepad.lnk")
$Shortcut.TargetPath = "$(Get-Location)\startup.bat"
$Shortcut.WorkingDirectory = "$(Get-Location)"
$Shortcut.WindowStyle = 7
$Shortcut.Save()