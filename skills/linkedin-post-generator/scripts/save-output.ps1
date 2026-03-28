[CmdletBinding(DefaultParameterSetName = "Content")]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("ideas", "post", "review")]
    [string]$Mode,

    [Parameter(ParameterSetName = "Content", Mandatory = $true)]
    [string]$Content,

    [Parameter(ParameterSetName = "File", Mandatory = $true)]
    [string]$InputFile,

    [string]$Slug = "draft",
    [string]$ProjectRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath)))
}

function Get-SafeSlug {
    param([string]$Value)

    $normalized = $Value.ToLowerInvariant()
    $normalized = [regex]::Replace($normalized, "[^a-z0-9]+", "-")
    $normalized = $normalized.Trim("-")

    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return "draft"
    }

    return $normalized
}

function Get-OutputSubdirectory {
    param([string]$CurrentMode)

    switch ($CurrentMode) {
        "ideas" { return "ideas" }
        "post" { return "ready-posts" }
        "review" { return "reviews" }
        default { throw "Unsupported mode: $CurrentMode" }
    }
}

if ($PSCmdlet.ParameterSetName -eq "File") {
    if (-not (Test-Path -LiteralPath $InputFile)) {
        throw "Input file not found: $InputFile"
    }

    $Content = Get-Content -LiteralPath $InputFile -Raw
}

$safeSlug = Get-SafeSlug -Value $Slug
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputDir = Join-Path (Join-Path $ProjectRoot "output") (Get-OutputSubdirectory -CurrentMode $Mode)

if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

$fileName = "{0}-{1}.md" -f $timestamp, $safeSlug
$outputPath = Join-Path $outputDir $fileName

Set-Content -LiteralPath $outputPath -Value $Content -Encoding UTF8

Write-Output $outputPath
