param(
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [string]$OutputDirectory = ""
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$compilerPath = Join-Path $projectRoot ".tools\tectonic\tectonic.exe"

if (-not (Test-Path -LiteralPath $compilerPath)) {
    throw "Tectonic compiler not found at $compilerPath"
}

$resolvedInput = Resolve-Path -LiteralPath $InputFile
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Split-Path -Parent $resolvedInput.Path
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
& $compilerPath --keep-logs --outdir $OutputDirectory $resolvedInput.Path

if ($LASTEXITCODE -ne 0) {
    throw "Tectonic failed with exit code $LASTEXITCODE"
}

$pdfName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedInput.Path) + ".pdf"
$pdfPath = Join-Path (Resolve-Path -LiteralPath $OutputDirectory).Path $pdfName
Write-Output "Compiled resume: $pdfPath"
