# PowerShell Script to Bootstrap Portable Python Environment for VRCOSC-Bilibili
$ErrorActionPreference = "Stop"

$PythonZipUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$GetPipUrl = "https://bootstrap.pypa.io/get-pip.py"

$ProjectRoot = $PSScriptRoot
$RuntimeDir = Join-Path $ProjectRoot "runtime"
$ZipFile = Join-Path $ProjectRoot "python_embed.zip"
$GetPipScript = Join-Path $ProjectRoot "get-pip.py"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

$InstalledHashFile = Join-Path $RuntimeDir "requirements.sha256"

# Function to compute hash of requirements.txt
function Get-RequirementsHash {
    if (Test-Path $RequirementsFile) {
        $hash = Get-FileHash -Path $RequirementsFile -Algorithm SHA256
        return $hash.Hash
    }
    return ""
}

$CurrentHash = Get-RequirementsHash

# 1. Check if python.exe already exists
if (Test-Path (Join-Path $RuntimeDir "python.exe")) {
    $HashMatch = $false
    if (Test-Path $InstalledHashFile) {
        $InstalledHash = Get-Content $InstalledHashFile -Raw
        if ($InstalledHash.Trim() -eq $CurrentHash) {
            $HashMatch = $true
        }
    }
    
    if ($HashMatch) {
        # Instant exit if everything matches
        exit 0
    }
    
    # Python exists but requirements don't match, run pip install to update
    Write-Host "Updating dependencies..." -ForegroundColor Cyan
    $PythonExe = Join-Path $RuntimeDir "python.exe"
    & $PythonExe -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -eq 0) {
        Set-Content $InstalledHashFile $CurrentHash
        Write-Host "[✓] Dependencies updated successfully." -ForegroundColor Green
    } else {
        Write-Error "Failed to update dependencies."
        exit 1
    }
    exit 0
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         Setting up VRCOSC-Bilibili environment           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "This will take a few minutes. Please keep this window open." -ForegroundColor Yellow
Write-Host ""

# 2. Download Python Embeddable Package
Write-Host "[1/4] Downloading Python 3.11.9 portable package..." -ForegroundColor Cyan
if (Test-Path $ZipFile) { Remove-Item $ZipFile }
$ProgressPreference = 'SilentlyContinue' # Disable progress bar for much faster download speed
Invoke-WebRequest -Uri $PythonZipUrl -OutFile $ZipFile
Write-Host "[✓] Download complete." -ForegroundColor Green

# 3. Extract Python
Write-Host "[2/4] Extracting Python to runtime folder..." -ForegroundColor Cyan
if (Test-Path $RuntimeDir) { Remove-Item -Recurse -Force $RuntimeDir }
New-Item -ItemType Directory -Path $RuntimeDir | Out-Null
Expand-Archive -Path $ZipFile -DestinationPath $RuntimeDir
Remove-Item $ZipFile
Write-Host "[✓] Extraction complete." -ForegroundColor Green

# 4. Enable site-packages in python311._pth
# By default, Python embeddable ignores site-packages. We must uncomment "import site".
Write-Host "[3/4] Configuring Python path settings..." -ForegroundColor Cyan
$PthFile = Join-Path $RuntimeDir "python311._pth"
if (Test-Path $PthFile) {
    $PthContent = Get-Content $PthFile
    $NewPthContent = @()
    foreach ($line in $PthContent) {
        if ($line -eq "#import site") {
            $NewPthContent += "import site"
        } else {
            $NewPthContent += $line
        }
    }
    Set-Content $PthFile $NewPthContent
    Write-Host "[✓] Configured python311._pth successfully." -ForegroundColor Green
} else {
    Write-Warning "Could not find python311._pth! site-packages may not work correctly."
}

# 5. Bootstrap pip
Write-Host "[4/4] Bootstrapping pip and installing dependencies..." -ForegroundColor Cyan
Write-Host "Downloading get-pip.py..." -ForegroundColor Cyan
if (Test-Path $GetPipScript) { Remove-Item $GetPipScript }
Invoke-WebRequest -Uri $GetPipUrl -OutFile $GetPipScript

Write-Host "Installing pip..." -ForegroundColor Cyan
$PythonExe = Join-Path $RuntimeDir "python.exe"
& $PythonExe $GetPipScript
Remove-Item $GetPipScript

# Verify pip was installed
Write-Host "Upgrading pip and installing required packages..." -ForegroundColor Cyan
& $PythonExe -m pip install --upgrade pip

# Install dependencies
& $PythonExe -m pip install -r $RequirementsFile
if ($LASTEXITCODE -eq 0) {
    $hash = Get-FileHash -Path $RequirementsFile -Algorithm SHA256
    Set-Content (Join-Path $RuntimeDir "requirements.sha256") $hash.Hash
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   [✓] Setup completed successfully!                      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
