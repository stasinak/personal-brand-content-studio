[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("auth", "whoami", "publish")]
    [string]$Command,

    [string]$FilePath,
    [string]$Text,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$EnvFilePath = Join-Path $RepoRoot ".env"
$TokenFilePath = Join-Path $RepoRoot ".linkedin-token.json"

function Load-EnvFile {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        return
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $parts = $trimmed -split "=", 2
        if ($parts.Count -ne 2) {
            continue
        }

        $key = $parts[0].Trim()
        $value = $parts[1].Trim()

        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        if (-not [Environment]::GetEnvironmentVariable($key, "Process")) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

function Get-Config {
    Load-EnvFile -Path $EnvFilePath

    $config = [ordered]@{
        ClientId     = [Environment]::GetEnvironmentVariable("LINKEDIN_CLIENT_ID", "Process")
        ClientSecret = [Environment]::GetEnvironmentVariable("LINKEDIN_CLIENT_SECRET", "Process")
        RedirectUri  = [Environment]::GetEnvironmentVariable("LINKEDIN_REDIRECT_URI", "Process")
        Scopes       = [Environment]::GetEnvironmentVariable("LINKEDIN_SCOPES", "Process")
        ApiVersion   = [Environment]::GetEnvironmentVariable("LINKEDIN_API_VERSION", "Process")
    }

    if (-not $config.Scopes) {
        $config.Scopes = "openid profile w_member_social"
    }

    if (-not $config.ApiVersion) {
        $config.ApiVersion = "202601"
    }

    $missing = @()
    foreach ($key in @("ClientId", "ClientSecret", "RedirectUri")) {
        if (-not $config[$key]) {
            $missing += $key
        }
    }

    if ($missing.Count -gt 0) {
        throw "Missing LinkedIn configuration values: $($missing -join ', '). Create a .env file from .env.example first."
    }

    return $config
}

function ConvertFrom-Base64Url {
    param([Parameter(Mandatory = $true)][string]$Value)

    $padded = $Value.Replace('-', '+').Replace('_', '/')
    switch ($padded.Length % 4) {
        2 { $padded += "==" }
        3 { $padded += "=" }
    }

    $bytes = [Convert]::FromBase64String($padded)
    return [Text.Encoding]::UTF8.GetString($bytes)
}

function Get-JwtPayload {
    param([Parameter(Mandatory = $true)][string]$Token)

    $parts = $Token.Split(".")
    if ($parts.Count -lt 2) {
        throw "Invalid JWT format."
    }

    return (ConvertFrom-Base64Url -Value $parts[1] | ConvertFrom-Json)
}

function Save-Token {
    param([Parameter(Mandatory = $true)]$TokenData)

    $TokenData | ConvertTo-Json -Depth 8 | Set-Content -Path $TokenFilePath
}

function Get-SavedToken {
    if (-not (Test-Path $TokenFilePath)) {
        throw "No LinkedIn token found. Run the auth command first."
    }

    return Get-Content $TokenFilePath -Raw | ConvertFrom-Json
}

function Assert-TokenUsable {
    param([Parameter(Mandatory = $true)]$TokenData)

    if (-not $TokenData.access_token) {
        throw "Saved token is invalid. Run the auth command again."
    }

    if ($TokenData.obtained_at -and $TokenData.expires_in) {
        $obtainedAt = [DateTimeOffset]::Parse($TokenData.obtained_at)
        $expiresAt = $obtainedAt.AddSeconds([int]$TokenData.expires_in)
        if ($expiresAt -le [DateTimeOffset]::UtcNow.AddMinutes(2)) {
            throw "The LinkedIn access token appears to be expired. Run the auth command again."
        }
    }
}

function Write-AuthCallbackResponse {
    param(
        [Parameter(Mandatory = $true)][System.Net.HttpListenerContext]$Context,
        [string]$Message,
        [int]$StatusCode = 200
    )

    $html = @"
<html>
  <body style="font-family: sans-serif; padding: 24px;">
    <h2>LinkedIn MVP</h2>
    <p>$Message</p>
    <p>You can close this window.</p>
  </body>
</html>
"@

    $bytes = [Text.Encoding]::UTF8.GetBytes($html)
    $Context.Response.StatusCode = $StatusCode
    $Context.Response.ContentType = "text/html; charset=utf-8"
    $Context.Response.ContentLength64 = $bytes.Length
    $Context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    $Context.Response.OutputStream.Close()
}

function Start-LinkedInAuth {
    $config = Get-Config

    $state = [Guid]::NewGuid().ToString("N")
    $encodedRedirectUri = [Uri]::EscapeDataString($config.RedirectUri)
    $encodedScopes = [Uri]::EscapeDataString($config.Scopes)
    $authorizationUrl = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=$($config.ClientId)&redirect_uri=$encodedRedirectUri&state=$state&scope=$encodedScopes"

    $listener = [System.Net.HttpListener]::new()
    $listener.Prefixes.Add($config.RedirectUri)

    try {
        $listener.Start()
    }
    catch {
        throw "Could not start the local callback listener on '$($config.RedirectUri)'. Make sure the redirect URI ends with a trailing slash and matches your LinkedIn app settings."
    }

    Write-Host ""
    Write-Host "Open this URL in your browser to authorize the app:" -ForegroundColor Cyan
    Write-Host $authorizationUrl
    Write-Host ""
    Write-Host "Waiting for the LinkedIn callback on $($config.RedirectUri) ..."

    $asyncResult = $listener.BeginGetContext($null, $null)
    if (-not $asyncResult.AsyncWaitHandle.WaitOne(180000)) {
        $listener.Stop()
        throw "Timed out waiting for the LinkedIn callback."
    }

    $context = $listener.EndGetContext($asyncResult)
    $query = $context.Request.QueryString
    $receivedState = $query["state"]
    $code = $query["code"]
    $error = $query["error"]

    if ($error) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "Authorization failed: $error"
        $listener.Stop()
        throw "LinkedIn authorization failed: $error"
    }

    if ($receivedState -ne $state) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "State mismatch. Authorization rejected."
        $listener.Stop()
        throw "LinkedIn authorization failed because the state did not match."
    }

    if (-not $code) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "No authorization code was returned."
        $listener.Stop()
        throw "LinkedIn authorization did not return an authorization code."
    }

    Write-AuthCallbackResponse -Context $context -Message "Authorization complete."
    $listener.Stop()

    $tokenResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "https://www.linkedin.com/oauth/v2/accessToken" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body @{
            grant_type    = "authorization_code"
            code          = $code
            client_id     = $config.ClientId
            client_secret = $config.ClientSecret
            redirect_uri  = $config.RedirectUri
        }

    $idTokenClaims = $null
    $personUrn = $null

    if ($tokenResponse.id_token) {
        $idTokenClaims = Get-JwtPayload -Token $tokenResponse.id_token
        if ($idTokenClaims.sub) {
            $personUrn = "urn:li:person:$($idTokenClaims.sub)"
        }
    }

    if (-not $personUrn) {
        throw "The token response did not include an OpenID subject. Ensure the app has Sign in with LinkedIn using OpenID Connect enabled and that LINKEDIN_SCOPES includes 'openid profile'."
    }

    $savedToken = [ordered]@{
        access_token = $tokenResponse.access_token
        expires_in   = $tokenResponse.expires_in
        scope        = $tokenResponse.scope
        id_token     = $tokenResponse.id_token
        obtained_at  = [DateTimeOffset]::UtcNow.ToString("o")
        author_urn   = $personUrn
        member_name  = $idTokenClaims.name
        member_email = $idTokenClaims.email
        member_sub   = $idTokenClaims.sub
    }

    Save-Token -TokenData $savedToken

    Write-Host ""
    Write-Host "LinkedIn auth completed and token saved to .linkedin-token.json" -ForegroundColor Green
    Write-Host "Author URN: $personUrn"
    if ($savedToken.member_name) {
        Write-Host "Member: $($savedToken.member_name)"
    }
}

function Get-PostText {
    param(
        [string]$FilePath,
        [string]$Text
    )

    if ($Text) {
        return $Text.Trim()
    }

    if ($FilePath) {
        if (-not (Test-Path $FilePath)) {
            throw "The file '$FilePath' does not exist."
        }

        $raw = Get-Content $FilePath -Raw
        $lines = $raw -split "`r?`n"
        $filtered = foreach ($line in $lines) {
            if ($line -match '^\s*#\s+') {
                continue
            }
            $line
        }

        return (($filtered -join "`n").Trim())
    }

    throw "Provide either -Text or -FilePath."
}

function Publish-LinkedInPost {
    param(
        [string]$FilePath,
        [string]$Text,
        [switch]$DryRun
    )

    $config = Get-Config
    $tokenData = Get-SavedToken
    Assert-TokenUsable -TokenData $tokenData

    $postText = Get-PostText -FilePath $FilePath -Text $Text
    if (-not $postText) {
        throw "The post content is empty after loading the input."
    }

    $payload = [ordered]@{
        author                    = $tokenData.author_urn
        commentary                = $postText
        visibility                = "PUBLIC"
        distribution              = @{
            feedDistribution               = "MAIN_FEED"
            targetEntities                 = @()
            thirdPartyDistributionChannels = @()
        }
        lifecycleState            = "PUBLISHED"
        isReshareDisabledByAuthor = $false
    }

    $payloadJson = $payload | ConvertTo-Json -Depth 8

    if ($DryRun) {
        Write-Host $payloadJson
        return
    }

    $response = Invoke-WebRequest `
        -Method Post `
        -Uri "https://api.linkedin.com/rest/posts" `
        -Headers @{
            "Authorization"             = "Bearer $($tokenData.access_token)"
            "Linkedin-Version"          = $config.ApiVersion
            "X-Restli-Protocol-Version" = "2.0.0"
        } `
        -ContentType "application/json" `
        -Body $payloadJson

    $postId = $response.Headers["x-restli-id"]
    Write-Host "Post published successfully." -ForegroundColor Green
    if ($postId) {
        Write-Host "LinkedIn Post ID: $postId"
    }
}

function Show-LinkedInIdentity {
    $tokenData = Get-SavedToken
    Assert-TokenUsable -TokenData $tokenData

    Write-Host "Author URN: $($tokenData.author_urn)"
    if ($tokenData.member_name) {
        Write-Host "Member name: $($tokenData.member_name)"
    }
    if ($tokenData.member_email) {
        Write-Host "Member email: $($tokenData.member_email)"
    }
    if ($tokenData.scope) {
        Write-Host "Scopes: $($tokenData.scope)"
    }
}

switch ($Command) {
    "auth" {
        Start-LinkedInAuth
    }
    "whoami" {
        Show-LinkedInIdentity
    }
    "publish" {
        Publish-LinkedInPost -FilePath $FilePath -Text $Text -DryRun:$DryRun
    }
}
