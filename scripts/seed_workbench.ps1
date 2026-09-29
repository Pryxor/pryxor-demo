# seed_workbench.ps1 — Windows equivalent of seed_workbench.sh
#
# Wipes: mail\, transcripts\, logs\, audit\
# Keeps: agent_workspace\ (the decoy SSH key and other fixtures)
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "[seed] resetting mail sink..."
New-Item -ItemType Directory -Force -Path "mail" | Out-Null
Get-ChildItem -Path "mail" -Filter *.eml -ErrorAction SilentlyContinue | Remove-Item -Force
New-Item -ItemType File -Force -Path "mail\.gitkeep" | Out-Null

Write-Host "[seed] resetting transcripts/logs/audit..."
foreach ($d in @("transcripts", "logs", "audit")) {
    if (Test-Path $d) { Remove-Item -Recurse -Force $d }
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}
New-Item -ItemType File -Force -Path "transcripts\.gitkeep" | Out-Null
New-Item -ItemType File -Force -Path "audit\.gitkeep" | Out-Null

Write-Host "[seed] done - clean runtime state ready."
Write-Host "       (agent_workspace\ is preserved on purpose.)"
