[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("auth", "list", "pull", "push-output")]
    [string]$Command,

    [string]$FilePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$EnvFilePath = Join-Path $RepoRoot ".env"
$TokenFilePath = Join-Path $RepoRoot ".google-drive-token.json"

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

function Get-DriveConfig {
    Load-EnvFile -Path $EnvFilePath

    $config = [ordered]@{
        ClientId       = [Environment]::GetEnvironmentVariable("GOOGLE_CLIENT_ID", "Process")
        ClientSecret   = [Environment]::GetEnvironmentVariable("GOOGLE_CLIENT_SECRET", "Process")
        RedirectUri    = [Environment]::GetEnvironmentVariable("GOOGLE_REDIRECT_URI", "Process")
        Scopes         = [Environment]::GetEnvironmentVariable("GOOGLE_SCOPES", "Process")
        IdeasFolderId  = [Environment]::GetEnvironmentVariable("GOOGLE_DRIVE_IDEAS_FOLDER_ID", "Process")
        PostFolderId   = [Environment]::GetEnvironmentVariable("GOOGLE_DRIVE_POST_FOLDER_ID", "Process")
        OutputFolderId = [Environment]::GetEnvironmentVariable("GOOGLE_DRIVE_OUTPUT_FOLDER_ID", "Process")
    }

    if (-not $config.RedirectUri) {
        $config.RedirectUri = "http://127.0.0.1:8766/"
    }

    if (-not $config.Scopes) {
        $config.Scopes = "https://www.googleapis.com/auth/drive"
    }

    $missing = @()
    foreach ($key in @("ClientId", "RedirectUri", "IdeasFolderId", "PostFolderId", "OutputFolderId")) {
        if (-not $config[$key]) {
            $missing += $key
        }
    }

    if ($missing.Count -gt 0) {
        throw "Missing Google Drive configuration values: $($missing -join ', '). Create a .env file from .env.example first."
    }

    return $config
}

function ConvertTo-Base64Url {
    param([byte[]]$Bytes)

    return [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function New-CodeVerifier {
    $bytes = New-Object byte[] 64
    [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    return ConvertTo-Base64Url -Bytes $bytes
}

function New-CodeChallenge {
    param([string]$Verifier)

    $sha = [Security.Cryptography.SHA256]::Create()
    $bytes = [Text.Encoding]::ASCII.GetBytes($Verifier)
    return ConvertTo-Base64Url -Bytes ($sha.ComputeHash($bytes))
}

function Save-DriveToken {
    param($TokenData)

    $TokenData | ConvertTo-Json -Depth 8 | Set-Content -Path $TokenFilePath
}

function Get-SavedDriveToken {
    if (-not (Test-Path $TokenFilePath)) {
        throw "No Google Drive token found. Run the auth command first."
    }

    return Get-Content $TokenFilePath -Raw | ConvertFrom-Json
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
    <h2>Google Drive MVP</h2>
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

function Start-DriveAuth {
    $config = Get-DriveConfig
    $state = [Guid]::NewGuid().ToString("N")
    $codeVerifier = New-CodeVerifier
    $codeChallenge = New-CodeChallenge -Verifier $codeVerifier

    $authQuery = @{
        client_id             = $config.ClientId
        redirect_uri          = $config.RedirectUri
        response_type         = "code"
        scope                 = $config.Scopes
        access_type           = "offline"
        include_granted_scopes = "true"
        prompt                = "consent"
        state                 = $state
        code_challenge        = $codeChallenge
        code_challenge_method = "S256"
    }

    $pairs = foreach ($key in $authQuery.Keys) {
        "$key=$([Uri]::EscapeDataString([string]$authQuery[$key]))"
    }
    $authorizationUrl = "https://accounts.google.com/o/oauth2/v2/auth?" + ($pairs -join "&")

    $listener = [System.Net.HttpListener]::new()
    $listener.Prefixes.Add($config.RedirectUri)

    try {
        $listener.Start()
    }
    catch {
        throw "Could not start the local callback listener on '$($config.RedirectUri)'. Make sure the redirect URI ends with a trailing slash and matches your Google OAuth client settings."
    }

    Write-Host ""
    Write-Host "Open this URL in your browser to authorize Google Drive access:" -ForegroundColor Cyan
    Write-Host $authorizationUrl
    Write-Host ""
    Write-Host "Waiting for the Google callback on $($config.RedirectUri) ..."

    $asyncResult = $listener.BeginGetContext($null, $null)
    if (-not $asyncResult.AsyncWaitHandle.WaitOne(180000)) {
        $listener.Stop()
        throw "Timed out waiting for the Google callback."
    }

    $context = $listener.EndGetContext($asyncResult)
    $query = $context.Request.QueryString
    $receivedState = $query["state"]
    $code = $query["code"]
    $error = $query["error"]

    if ($error) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "Authorization failed: $error"
        $listener.Stop()
        throw "Google authorization failed: $error"
    }

    if ($receivedState -ne $state) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "State mismatch. Authorization rejected."
        $listener.Stop()
        throw "Google authorization failed because the state did not match."
    }

    if (-not $code) {
        Write-AuthCallbackResponse -Context $context -StatusCode 400 -Message "No authorization code was returned."
        $listener.Stop()
        throw "Google authorization did not return an authorization code."
    }

    Write-AuthCallbackResponse -Context $context -Message "Authorization complete."
    $listener.Stop()

    $tokenBody = @{
        client_id     = $config.ClientId
        code          = $code
        code_verifier = $codeVerifier
        grant_type    = "authorization_code"
        redirect_uri  = $config.RedirectUri
    }

    if ($config.ClientSecret) {
        $tokenBody.client_secret = $config.ClientSecret
    }

    $tokenResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "https://oauth2.googleapis.com/token" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $tokenBody

    $savedToken = [ordered]@{
        access_token  = $tokenResponse.access_token
        expires_in    = $tokenResponse.expires_in
        refresh_token = $tokenResponse.refresh_token
        scope         = $tokenResponse.scope
        token_type    = $tokenResponse.token_type
        obtained_at   = [DateTimeOffset]::UtcNow.ToString("o")
    }

    Save-DriveToken -TokenData $savedToken

    Write-Host ""
    Write-Host "Google Drive auth completed and token saved to .google-drive-token.json" -ForegroundColor Green
}

function Refresh-DriveAccessToken {
    param(
        [Parameter(Mandatory = $true)]$TokenData,
        [Parameter(Mandatory = $true)]$Config
    )

    if (-not $TokenData.refresh_token) {
        throw "No refresh token is available. Run the auth command again."
    }

    $body = @{
        client_id     = $Config.ClientId
        refresh_token = $TokenData.refresh_token
        grant_type    = "refresh_token"
    }

    if ($Config.ClientSecret) {
        $body.client_secret = $Config.ClientSecret
    }

    $tokenResponse = Invoke-RestMethod `
        -Method Post `
        -Uri "https://oauth2.googleapis.com/token" `
        -ContentType "application/x-www-form-urlencoded" `
        -Body $body

    $TokenData.access_token = $tokenResponse.access_token
    $TokenData.expires_in = $tokenResponse.expires_in
    $TokenData.obtained_at = [DateTimeOffset]::UtcNow.ToString("o")
    Save-DriveToken -TokenData $TokenData
    return $TokenData
}

function Get-ValidDriveAccessToken {
    $config = Get-DriveConfig
    $tokenData = Get-SavedDriveToken

    if (-not $tokenData.access_token) {
        return (Refresh-DriveAccessToken -TokenData $tokenData -Config $config).access_token
    }

    if ($tokenData.obtained_at -and $tokenData.expires_in) {
        $obtainedAt = [DateTimeOffset]::Parse($tokenData.obtained_at)
        $expiresAt = $obtainedAt.AddSeconds([int]$tokenData.expires_in)
        if ($expiresAt -le [DateTimeOffset]::UtcNow.AddMinutes(2)) {
            return (Refresh-DriveAccessToken -TokenData $tokenData -Config $config).access_token
        }
    }

    return $tokenData.access_token
}

function Invoke-DriveJsonRequest {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri
    )

    $accessToken = Get-ValidDriveAccessToken
    try {
        return Invoke-RestMethod `
            -Method $Method `
            -Uri $Uri `
            -Headers @{ Authorization = "Bearer $accessToken" }
    }
    catch {
        $response = $_.Exception.Response
        if ($response -and $response.GetResponseStream()) {
            $reader = New-Object IO.StreamReader($response.GetResponseStream())
            $body = $reader.ReadToEnd()
            throw "Google Drive API request failed. URI: $Uri`nResponse: $body"
        }
        throw
    }
}

function Invoke-DriveBinaryDownload {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$OutFile
    )

    $accessToken = Get-ValidDriveAccessToken
    try {
        Invoke-WebRequest `
            -Method Get `
            -Uri $Uri `
            -Headers @{ Authorization = "Bearer $accessToken" } `
            -OutFile $OutFile | Out-Null
    }
    catch {
        $response = $_.Exception.Response
        if ($response -and $response.GetResponseStream()) {
            $reader = New-Object IO.StreamReader($response.GetResponseStream())
            $body = $reader.ReadToEnd()
            throw "Google Drive download failed. URI: $Uri`nResponse: $body"
        }
        throw
    }
}

function Get-DriveFolderItems {
    param([Parameter(Mandatory = $true)][string]$FolderId)

    $query = "'$FolderId' in parents and trashed = false"
    $uri = "https://www.googleapis.com/drive/v3/files?q=$([Uri]::EscapeDataString($query))&fields=files(id,name,mimeType,modifiedTime,size)"
    $response = Invoke-DriveJsonRequest -Method Get -Uri $uri
    return @($response.files)
}

function Get-ExportSpec {
    param(
        [Parameter(Mandatory = $true)][string]$MimeType,
        [Parameter(Mandatory = $true)][string]$Category
    )

    switch ($MimeType) {
        "application/vnd.google-apps.document" {
            if ($Category -eq "post") {
                return @{ MimeType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"; Extension = ".docx" }
            }
            return @{ MimeType = "text/markdown"; Extension = ".md" }
        }
        "application/vnd.google-apps.spreadsheet" {
            return @{ MimeType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"; Extension = ".xlsx" }
        }
        default {
            return $null
        }
    }
}

function Ensure-FolderExists {
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Sync-DriveFolderToLocal {
    param(
        [Parameter(Mandatory = $true)][string]$FolderId,
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [Parameter(Mandatory = $true)][string]$Category
    )

    Ensure-FolderExists -Path $LocalPath
    $items = Get-DriveFolderItems -FolderId $FolderId

    foreach ($item in $items) {
        if ($item.mimeType -eq "application/vnd.google-apps.folder") {
            continue
        }

        $targetName = $item.name
        $downloadUri = $null

        if ($item.mimeType.StartsWith("application/vnd.google-apps.")) {
            $exportSpec = Get-ExportSpec -MimeType $item.mimeType -Category $Category
            if (-not $exportSpec) {
                Write-Host "Skipping unsupported Google Workspace file: $($item.name) [$($item.mimeType)]" -ForegroundColor Yellow
                continue
            }

            if (-not [IO.Path]::GetExtension($targetName)) {
                $targetName += $exportSpec.Extension
            }

            $downloadUri = "https://www.googleapis.com/drive/v3/files/$($item.id)/export?mimeType=$([Uri]::EscapeDataString($exportSpec.MimeType))"
        }
        else {
            $downloadUri = "https://www.googleapis.com/drive/v3/files/$($item.id)?alt=media"
        }

        $targetPath = Join-Path $LocalPath $targetName
        Invoke-DriveBinaryDownload -Uri $downloadUri -OutFile $targetPath
        Write-Host "Downloaded: $targetPath"
    }
}

function Get-ExistingDriveFileByName {
    param(
        [Parameter(Mandatory = $true)][string]$FolderId,
        [Parameter(Mandatory = $true)][string]$FileName
    )

    $escapedName = $FileName.Replace("'", "\'")
    $query = "'$FolderId' in parents and name = '$escapedName' and trashed = false"
    $uri = "https://www.googleapis.com/drive/v3/files?q=$([Uri]::EscapeDataString($query))&fields=files(id,name)"
    $response = Invoke-DriveJsonRequest -Method Get -Uri $uri
    return @($response.files) | Select-Object -First 1
}

function Invoke-DriveMultipartUpload {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Uri,
        [Parameter(Mandatory = $true)][string]$MetadataJson,
        [Parameter(Mandatory = $true)][byte[]]$FileBytes,
        [Parameter(Mandatory = $true)][string]$FileContentType
    )

    $boundary = "===============DriveBoundary$([Guid]::NewGuid().ToString('N'))"
    $newline = "`r`n"

    $prefix = (
        "--$boundary$newline" +
        "Content-Type: application/json; charset=UTF-8$newline$newline" +
        "$MetadataJson$newline" +
        "--$boundary$newline" +
        "Content-Type: $FileContentType$newline$newline"
    )
    $suffix = "$newline--$boundary--$newline"

    $prefixBytes = [Text.Encoding]::UTF8.GetBytes($prefix)
    $suffixBytes = [Text.Encoding]::UTF8.GetBytes($suffix)
    $body = New-Object byte[] ($prefixBytes.Length + $FileBytes.Length + $suffixBytes.Length)

    [Array]::Copy($prefixBytes, 0, $body, 0, $prefixBytes.Length)
    [Array]::Copy($FileBytes, 0, $body, $prefixBytes.Length, $FileBytes.Length)
    [Array]::Copy($suffixBytes, 0, $body, $prefixBytes.Length + $FileBytes.Length, $suffixBytes.Length)

    $accessToken = Get-ValidDriveAccessToken

    try {
        return Invoke-RestMethod `
            -Method $Method `
            -Uri $Uri `
            -Headers @{
                Authorization = "Bearer $accessToken"
                "Content-Type" = "multipart/related; boundary=$boundary"
            } `
            -Body $body
    }
    catch {
        $response = $_.Exception.Response
        if ($response -and $response.GetResponseStream()) {
            $reader = New-Object IO.StreamReader($response.GetResponseStream())
            $bodyText = $reader.ReadToEnd()
            throw "Google Drive upload failed. URI: $Uri`nResponse: $bodyText"
        }
        throw
    }
}

function Push-OutputFileToDrive {
    param([string]$FilePath)

    $config = Get-DriveConfig

    if ($FilePath) {
        $resolvedFiles = @(Resolve-Path $FilePath | ForEach-Object { $_.Path })
    }
    else {
        $resolvedFiles = @(Get-ChildItem -Path (Join-Path $RepoRoot "output") -File -Filter *.md | ForEach-Object { $_.FullName })
    }

    if ($resolvedFiles.Count -eq 0) {
        throw "No output files found to upload."
    }

    foreach ($resolved in $resolvedFiles) {
        $fileName = Split-Path -Leaf $resolved
        $fileBytes = [IO.File]::ReadAllBytes($resolved)
        $existing = Get-ExistingDriveFileByName -FolderId $config.OutputFolderId -FileName $fileName

        if ($existing) {
            $metadataJson = (@{ name = $fileName } | ConvertTo-Json -Compress)
            $uri = "https://www.googleapis.com/upload/drive/v3/files/$($existing.id)?uploadType=multipart"
            Invoke-DriveMultipartUpload `
                -Method Patch `
                -Uri $uri `
                -MetadataJson $metadataJson `
                -FileBytes $fileBytes `
                -FileContentType "text/markdown; charset=UTF-8" | Out-Null
            Write-Host "Updated Drive file: $fileName"
        }
        else {
            $metadataJson = (@{ name = $fileName; parents = @($config.OutputFolderId) } | ConvertTo-Json -Compress)
            $uri = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
            Invoke-DriveMultipartUpload `
                -Method Post `
                -Uri $uri `
                -MetadataJson $metadataJson `
                -FileBytes $fileBytes `
                -FileContentType "text/markdown; charset=UTF-8" | Out-Null
            Write-Host "Uploaded Drive file: $fileName"
        }
    }
}

function Show-ConfiguredDriveFolders {
    $config = Get-DriveConfig
    $folders = @(
        @{ Name = "ideas"; Id = $config.IdeasFolderId },
        @{ Name = "post"; Id = $config.PostFolderId },
        @{ Name = "output"; Id = $config.OutputFolderId }
    )

    foreach ($folder in $folders) {
        Write-Host ""
        Write-Host "$($folder.Name) [$($folder.Id)]" -ForegroundColor Cyan
        $items = Get-DriveFolderItems -FolderId $folder.Id
        foreach ($item in $items) {
            Write-Host " - $($item.name) [$($item.mimeType)]"
        }
    }
}

function Pull-DriveFolders {
    $config = Get-DriveConfig

    Sync-DriveFolderToLocal -FolderId $config.IdeasFolderId -LocalPath (Join-Path $RepoRoot "ideas") -Category "ideas"
    Sync-DriveFolderToLocal -FolderId $config.PostFolderId -LocalPath (Join-Path $RepoRoot "post") -Category "post"
    Sync-DriveFolderToLocal -FolderId $config.OutputFolderId -LocalPath (Join-Path $RepoRoot "output") -Category "output"
}

switch ($Command) {
    "auth" {
        Start-DriveAuth
    }
    "list" {
        Show-ConfiguredDriveFolders
    }
    "pull" {
        Pull-DriveFolders
    }
    "push-output" {
        Push-OutputFileToDrive -FilePath $FilePath
    }
}
