# Hide console window
$code = '[DllImport("user32.dll")] public static extern bool ShowWindow(int handle, int state);'
$win32 = Add-Type -MemberDefinition $code -Name "Win32" -Namespace "Win32Functions" -PassThru
$win32::ShowWindow((Get-Process -Id $PID).MainWindowHandle, 0) | Out-Null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$form = New-Object System.Windows.Forms.Form
$form.Text = "VRCOSC-Bilibili"
$form.Size = New-Object System.Drawing.Size(450, 180)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true
$form.BackColor = [System.Drawing.Color]::FromArgb(255, 40, 40, 40)
$form.ForeColor = [System.Drawing.Color]::White

$label = New-Object System.Windows.Forms.Label
$label.Text = "Starting VRCOSC-Bilibili..."
$label.Location = New-Object System.Drawing.Point(20, 20)
$label.AutoSize = $true
$label.Font = New-Object System.Drawing.Font("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($label)

$status = New-Object System.Windows.Forms.Label
$status.Text = "Initializing..."
$status.Location = New-Object System.Drawing.Point(20, 60)
$status.Size = New-Object System.Drawing.Size(400, 40)
$status.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$form.Controls.Add($status)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20, 100)
$progressBar.Size = New-Object System.Drawing.Size(395, 15)
$progressBar.Style = "Marquee"
$form.Controls.Add($progressBar)

$form.Show()
$form.Refresh()

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $baseDir

function Update-Status($msg) {
    $status.Text = $msg
    $form.Refresh()
}

Update-Status "Locating Python installation..."
$python = "python"
try {
    $pyVersion = & $python --version 2>&1
} catch {
    Update-Status "Error: Python is not installed or not in your system PATH. Please install Python 3.10+."
    $progressBar.Style = "Blocks"
    Start-Sleep -Seconds 10
    $form.Close()
    exit
}

$venvPath = Join-Path $baseDir ".venv"
$isFirstRun = -not (Test-Path $venvPath)

if ($isFirstRun) {
    Update-Status "First startup detected. Creating isolated Python environment... (This may take a minute)"
    & $python -m venv $venvPath
} else {
    Update-Status "Checking existing environment..."
}

$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

if ($isFirstRun) {
    Update-Status "Downloading and installing dependencies... (Please wait)"
    $proc = Start-Process -FilePath $pipExe -ArgumentList "install -r requirements.txt" -NoNewWindow -Wait -PassThru
} else {
    Update-Status "Verifying dependencies in the background..."
    # Run silently in background to ensure everything is up to date
    $proc = Start-Process -FilePath $pipExe -ArgumentList "install -r requirements.txt" -WindowStyle Hidden -Wait -PassThru
}

Update-Status "Starting the web server..."
# Start the backend server hidden
$procApp = Start-Process -FilePath $pythonExe -ArgumentList "backend\main.py" -WindowStyle Hidden -PassThru

# Wait briefly for the server to start and trigger the browser
Start-Sleep -Seconds 3

$form.Close()
