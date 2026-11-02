param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateNotNullOrEmpty()]
    [string]$ProgramName
)

$ErrorActionPreference = 'Stop'

if ([System.IO.Path]::GetExtension($ProgramName) -ieq '.DZX') {
    $ProgramName = [System.IO.Path]::ChangeExtension($ProgramName, $null)
}

if ([System.IO.Path]::IsPathRooted($ProgramName)) {
    $sourcePath = [System.IO.Path]::GetFullPath("$ProgramName.DZX")
} else {
    $sourcePath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) "$ProgramName.DZX"))
}

if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "ZX-81 source not found: $sourcePath"
}

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repositoryRoot = Split-Path -Parent $scriptDirectory
$badigPath = Join-Path $repositoryRoot 'badig.py'
$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

& $python $badigPath $sourcePath '-id' 'zx81' '--tk_tokenize'
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$asciiPath = [System.IO.Path]::ChangeExtension($sourcePath, '.AZX')
$programPath = [System.IO.Path]::ChangeExtension($sourcePath, '.p')
if (-not (Test-Path -LiteralPath $asciiPath -PathType Leaf)) {
    throw "Numbered ASCII output not found: $asciiPath"
}
if (-not (Test-Path -LiteralPath $programPath -PathType Leaf)) {
    throw "Tokenized output not found: $programPath"
}

Write-Host "Created $asciiPath"
Write-Host "Created $programPath"