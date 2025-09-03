<#
.SYNOPSIS
    Batch convert markdown files to HTML using md2html
.DESCRIPTION
    Ultra-clean wrapper for md2html converter with explicit configuration and no fallbacks
.PARAMETER InputDir
    Directory containing markdown files to convert
.PARAMETER OutputDir
    Directory where HTML files will be saved
.PARAMETER Theme
    Theme name: manaforge, github, minimal, or dark
.PARAMETER Recursive
    Process subdirectories recursively
.PARAMETER TableOfContents
    Generate table of contents in HTML
.PARAMETER Watch
    Enable watch mode for continuous conversion
.PARAMETER Serve
    Start preview server after conversion
.PARAMETER Port
    Server port (default: 8000, used with -Serve)
.EXAMPLE
    .\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme github
.EXAMPLE
    .\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme manaforge -Recursive -TableOfContents
.EXAMPLE
    .\Convert-MdBatch.ps1 -InputDir docs -OutputDir site -Theme dark -Serve -Port 3000
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateScript({Test-Path $_ -PathType Container})]
    [string]$InputDir,
    
    [Parameter(Mandatory=$true, Position=1)]
    [string]$OutputDir,
    
    [Parameter(Mandatory=$true, Position=2)]
    [ValidateSet('manaforge', 'github', 'minimal', 'dark')]
    [string]$Theme,
    
    [Parameter()]
    [switch]$Recursive,
    
    [Parameter()]
    [Alias('TOC')]
    [switch]$TableOfContents,
    
    [Parameter()]
    [switch]$Watch,
    
    [Parameter()]
    [switch]$Serve,
    
    [Parameter()]
    [int]$Port = 8000
)

# Script configuration
$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
$Md2HtmlPath = Join-Path $ScriptDir "md2html.py"

# Color functions
function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "ERROR: " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host "SUCCESS: " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-InfoMessage {
    param([string]$Message)
    Write-Host "INFO: " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "WARNING: " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

# Function to check Python availability
function Test-Python {
    $pythonCmd = $null
    
    # Try python3 first, then python
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } else {
        Write-ErrorMessage "Python is not installed or not in PATH"
        exit 1
    }
    
    # Check Python version
    $versionOutput = & $pythonCmd --version 2>&1
    if ($versionOutput -match "Python (\d+)\.(\d+)") {
        $majorVersion = [int]$Matches[1]
        $minorVersion = [int]$Matches[2]
        
        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 9)) {
            Write-ErrorMessage "Python 3.9 or higher is required (found: $versionOutput)"
            exit 1
        }
        
        Write-InfoMessage "Using Python: $pythonCmd (version $majorVersion.$minorVersion)"
    }
    
    return $pythonCmd
}

# Function to check md2html availability
function Test-Md2Html {
    param([string]$PythonCmd)
    
    if (-not (Test-Path $Md2HtmlPath)) {
        Write-ErrorMessage "md2html.py not found at: $Md2HtmlPath"
        Write-InfoMessage "Please ensure the md2html converter is installed"
        exit 1
    }
    
    # Check dependencies
    Write-InfoMessage "Checking dependencies..."
    $checkDeps = @"
try:
    import click, markdown, bs4, watchdog, aiohttp
    print('OK')
except ImportError as e:
    print(f'MISSING: {e.name}')
"@
    
    $result = & $PythonCmd -c $checkDeps 2>&1
    if ($result -ne 'OK') {
        Write-ErrorMessage "Missing required Python packages"
        Write-InfoMessage "Install with: pip install click markdown beautifulsoup4 watchdog aiohttp"
        exit 1
    }
}

# Function to validate directories
function Test-Directories {
    param(
        [string]$InputDirectory,
        [string]$OutputDirectory
    )
    
    # Check input directory
    if (-not (Test-Path $InputDirectory -PathType Container)) {
        Write-ErrorMessage "Input directory not found: $InputDirectory"
        exit 1
    }
    
    # Check for markdown files
    $mdFiles = Get-ChildItem -Path $InputDirectory -Filter "*.md" -File
    if ($mdFiles.Count -eq 0) {
        Write-WarningMessage "No markdown files found in: $InputDirectory"
        if (-not $Recursive) {
            Write-InfoMessage "Use -Recursive flag to search subdirectories"
        }
    }
    
    # Create output directory if needed
    if (-not (Test-Path $OutputDirectory)) {
        Write-InfoMessage "Creating output directory: $OutputDirectory"
        New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    }
}

# Main execution
function Main {
    Write-Host "=== MD2HTML Batch Converter ===" -ForegroundColor Cyan
    Write-Host ""
    
    # Perform checks
    $pythonCmd = Test-Python
    Test-Md2Html -PythonCmd $pythonCmd
    Test-Directories -InputDirectory $InputDir -OutputDirectory $OutputDir
    
    # Build command arguments
    $arguments = @()
    
    if ($Watch) {
        # Watch mode
        Write-InfoMessage "Starting watch mode..."
        Write-InfoMessage "Input: $InputDir"
        Write-InfoMessage "Output: $OutputDir"
        Write-InfoMessage "Theme: $Theme"
        Write-InfoMessage "Press Ctrl+C to stop"
        
        $arguments = @("watch", $InputDir, "--output", $OutputDir, "--theme", $Theme)
        if ($Recursive) { $arguments += "--recursive" }
        
    } else {
        # Convert mode
        Write-InfoMessage "Converting markdown files..."
        Write-InfoMessage "Input: $InputDir"
        Write-InfoMessage "Output: $OutputDir"
        Write-InfoMessage "Theme: $Theme"
        
        $arguments = @("convert", $InputDir, "--output", $OutputDir, "--theme", $Theme)
        if ($Recursive) { $arguments += "--recursive" }
        if ($TableOfContents) { $arguments += "--toc" }
    }
    
    # Execute md2html
    try {
        $process = Start-Process -FilePath $pythonCmd -ArgumentList (@($Md2HtmlPath) + $arguments) -NoNewWindow -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-SuccessMessage "Conversion completed successfully!"
            
            # Start server if requested
            if ($Serve -and -not $Watch) {
                Write-InfoMessage "Starting preview server..."
                Write-InfoMessage "URL: http://127.0.0.1:$Port"
                Write-InfoMessage "Press Ctrl+C to stop"
                
                & $pythonCmd $Md2HtmlPath serve $OutputDir --port $Port
            }
        } else {
            Write-ErrorMessage "Conversion failed with exit code: $($process.ExitCode)"
            exit 1
        }
    } catch {
        Write-ErrorMessage "An error occurred: $_"
        exit 1
    }
}

# Show banner
Write-Host @"
╔══════════════════════════════════════╗
║     MD2HTML Batch Converter v2.0     ║
║   Ultra-clean, no fallbacks, explicit║
╚══════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Run main function
Main