# BRAINS Research Skill - PowerShell installer
[CmdletBinding()]
param(
    [string]$ResearchRoot = "",
    [string]$ClaudeHome = (Join-Path $env:USERPROFILE ".claude")
)

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "BRAINS Research Skill installer" -ForegroundColor Cyan
Write-Host "Repo root:    $RepoRoot"
Write-Host "Claude home:  $ClaudeHome"
Write-Host ""

# 1. config.json
$cfgPath = Join-Path $RepoRoot "config.json"
$cfgExample = Join-Path $RepoRoot "config.json.example"
if (-not (Test-Path $cfgPath)) {
    Copy-Item $cfgExample $cfgPath
    Write-Host "Created config.json from config.json.example."
    if ($ResearchRoot -eq "") {
        $ResearchRoot = Read-Host "Research root path (Enter to keep default '\\192.168.1.101\Singularity_Backup\Research')"
    }
    if ($ResearchRoot -ne "") {
        $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
        $cfg.research_root = $ResearchRoot
        $cfg | ConvertTo-Json -Depth 5 | Set-Content $cfgPath -Encoding utf8
        Write-Host "research_root set to: $($cfg.research_root)"
    }
} else {
    Write-Host "config.json already exists - keeping it."
}

# 2. Validate research_root
$cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
if (-not (Test-Path $cfg.research_root)) {
    Write-Warning "research_root does not exist or is unreachable: $($cfg.research_root)"
    Write-Warning "The skill will not run until this path is reachable."
}

# 3. Create venv and install
$venv = Join-Path $RepoRoot ".venv"
if (-not (Test-Path $venv)) {
    Write-Host "Creating virtualenv..."
    python -m venv $venv
}
$pip = Join-Path $venv "Scripts\python.exe"
& $pip -m pip install --upgrade pip 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Error "pip install --upgrade pip failed"; exit 1 }
& $pip -m pip install -e "${RepoRoot}[dev]" 2>&1 | Tee-Object -Variable pipOut | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host $pipOut; Write-Error "pip install -e failed"; exit 1 }

# 4. Install skill bundle (whitelist - only copy what the skill needs at runtime)
$skillDir = Join-Path $ClaudeHome "skills\brains-research"
if (Test-Path $skillDir) { Remove-Item -Recurse -Force $skillDir }
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
$skillFiles = @("SKILL.md", "config.json", "config.json.example", "LICENSE", "README.md", "pyproject.toml")
foreach ($f in $skillFiles) {
    $src = Join-Path $RepoRoot $f
    if (Test-Path $src) { Copy-Item -Force $src (Join-Path $skillDir $f) }
}
foreach ($d in @("scripts", "references", "commands")) {
    Copy-Item -Recurse -Force (Join-Path $RepoRoot $d) (Join-Path $skillDir $d)
}
Write-Host "Skill installed at: $skillDir"

# 5. Install slash commands
$cmdsDir = Join-Path $ClaudeHome "commands"
New-Item -ItemType Directory -Force -Path $cmdsDir | Out-Null
Copy-Item -Force (Join-Path $RepoRoot "commands\brains-research-process.md") $cmdsDir
Copy-Item -Force (Join-Path $RepoRoot "commands\brains-research-status.md") $cmdsDir
Write-Host "Slash commands installed at: $cmdsDir"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Try: /brains-research-status"
