# Sets HWiNFO's sensor polling interval (SensorInterval, ms) and restarts HWiNFO.
# install.ps1 copies this file to "%ProgramFiles%\HWiNFO Panel\" (administrators only); the "SetInterval" task
# runs it through hidden.vbs. The value is read from a user-writable file but only accepted as a plain integer
# and clamped to 250..60000 ms.
param(
    [Parameter(Mandatory)][string]$Exe,       # full path of HWiNFO64.EXE
    [Parameter(Mandatory)][string]$ValFile    # text file containing the interval in ms
)
if ((Split-Path $Exe -Leaf) -ne 'HWiNFO64.EXE' -or -not (Test-Path -LiteralPath $Exe -PathType Leaf)) { exit 2 }
$ini = Join-Path (Split-Path $Exe) 'HWiNFO64.INI'

$raw = (Get-Content -LiteralPath $ValFile -Raw -ErrorAction Stop).Trim()
if ($raw -notmatch '^\d{1,6}$') { exit 1 }
$ms = [Math]::Min(60000, [Math]::Max(250, [int]$raw))

Stop-Process -Name HWiNFO64 -Force -ErrorAction SilentlyContinue
for ($i = 0; $i -lt 50 -and (Get-Process HWiNFO64 -ErrorAction SilentlyContinue); $i++) { Start-Sleep -Milliseconds 100 }

$lines = New-Object 'System.Collections.Generic.List[string]'
if (Test-Path -LiteralPath $ini) { foreach ($l in (Get-Content -LiteralPath $ini)) { $lines.Add($l) } }
$idx = $lines.FindIndex([Predicate[string]]{ param($l) $l -match '^SensorInterval=' })
if ($idx -ge 0) { $lines[$idx] = "SensorInterval=$ms" }
else {
    $s = $lines.FindIndex([Predicate[string]]{ param($l) $l -match '^\[Settings\]' })
    if ($s -ge 0) { $lines.Insert($s + 1, "SensorInterval=$ms") } else { $lines.Add('[Settings]'); $lines.Add("SensorInterval=$ms") }
}
Set-Content -LiteralPath $ini -Value $lines -Encoding Ascii

Start-Process -FilePath $Exe -WorkingDirectory (Split-Path $Exe)
