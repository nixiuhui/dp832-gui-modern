$ErrorActionPreference = "Stop"
$root = "d:\Program Files\dp832-gui-master"
$pythonw = Join-Path $root ".venv\Scripts\pythonw.exe"
$script  = Join-Path $root "dp832gui\dpgui.py"
$workdir = Join-Path $root "dp832gui"
$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = Join-Path $desktop "DP832 GUI.lnk"

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($lnkPath)
$sc.TargetPath = $pythonw
$sc.Arguments = '"' + $script + '"'
$sc.WorkingDirectory = $workdir
$sc.IconLocation = $pythonw + ",0"
$sc.Description = "Rigol DP832 电源监控 GUI"
$sc.Save()

Write-Output ("Shortcut created: " + $lnkPath)
