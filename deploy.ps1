# PowerShell script to create a proper Lambda deployment ZIP
# Run from PowerShell: .\deploy.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Creating AWS Lambda Deployment ZIP ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "Error: app.py not found. Please run from project root." -ForegroundColor Red
    exit 1
}

# Verify templates exist
if (-not (Test-Path "templates\auth.html")) {
    Write-Host "Error: templates\auth.html not found!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "templates\index.html")) {
    Write-Host "Error: templates\index.html not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Template files found" -ForegroundColor Green

# Define zip path
$zipPath = "deployment.zip"

# Remove old zip if exists
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
    Write-Host "Removed old deployment.zip"
}

# Create list of files to include
$filesToInclude = @(
    "app.py",
    "auth_integration.py",
    "models.py",
    "requirements.txt",
    "MANIFEST.in"
)

# Create ZIP
Write-Host "Creating ZIP file..." -ForegroundColor Yellow
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
    (Get-Item ".").FullName,
    $zipPath,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $false
)

# But this zips everything. Let's do it the proper way:
# We need to manually create the ZIP with only selected files

# Alternative: Use 7zip or manual approach
Write-Host "Creating deployment with Compress-Archive..." -ForegroundColor Yellow

# Remove the full-directory zip we just made
Remove-Item $zipPath -Force

# Create temporary folder
$tempDir = "temp_deploy"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files to temp folder
Write-Host "Copying files to temporary folder..." -ForegroundColor Gray
Copy-Item "app.py" $tempDir\
Copy-Item "auth_integration.py" $tempDir\
Copy-Item "models.py" $tempDir\
Copy-Item "requirements.txt" $tempDir\
Copy-Item "MANIFEST.in" $tempDir\

# Copy folders
Write-Host "Copying templates folder..." -ForegroundColor Gray
Copy-Item "templates" $tempDir\ -Recurse
Write-Host "Copying static folder..." -ForegroundColor Gray
if (Test-Path "static") {
    Copy-Item "static" $tempDir\ -Recurse
}
Write-Host "Copying data folder (if exists)..." -ForegroundColor Gray
if (Test-Path "data") {
    Copy-Item "data" $tempDir\ -Recurse
}

# Create the ZIP
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Cleanup
Remove-Item $tempDir -Recurse -Force

Write-Host "" -ForegroundColor Green
Write-Host "✓ Deployment ZIP created: deployment.zip" -ForegroundColor Green

# Verify
Write-Host "Verifying ZIP contents..." -ForegroundColor Cyan
$zipContents = [System.IO.Compression.ZipFile]::OpenRead($zipPath).Entries.Name | Sort-Object -Unique
$hasAuthHtml = $zipContents -contains "templates/auth.html"
$hasIndexHtml = $zipContents -contains "templates/index.html"
$hasAuthIntegration = $zipContents -contains "auth_integration.py"

Write-Host "  Templates/auth.html: " -NoNewline
if ($hasAuthHtml) { Write-Host "✓ FOUND" -ForegroundColor Green } else { Write-Host "✗ MISSING" -ForegroundColor Red }
Write-Host "  Templates/index.html: " -NoNewline
if ($hasIndexHtml) { Write-Host "✓ FOUND" -ForegroundColor Green } else { Write-Host "✗ MISSING" -ForegroundColor Red }
Write-Host "  auth_integration.py: " -NoNewline
if ($hasAuthIntegration) { Write-Host "✓ FOUND" -ForegroundColor Green } else { Write-Host "✗ MISSING" -ForegroundColor Red }

Write-Host ""

if ($hasAuthHtml -and $hasIndexHtml -and $hasAuthIntegration) {
    Write-Host "✓ ZIP is ready for deployment!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Upload deployment.zip to AWS Lambda"
    Write-Host "2. Set handler to: app.app"
    Write-Host "3. Set runtime to: Python 3.11"
    Write-Host "4. Configure environment variables"
    Write-Host "5. Connect API Gateway (if needed)"
} else {
    Write-Host "✗ ZIP is missing critical files!" -ForegroundColor Red
    Write-Host "Check the output above and fix before deploying."
    exit 1
}
