<#
.DESCRIPTION
    Deprecated Installation Bootstrap

.Notes
This file only exists for backwards compatibility reasons. Cannot be deleted. Should not be modified.
#>

param(
    [Parameter(
        Mandatory = $false
    )]
    [string]$version = "develop" ## use latest if no version was given
    , [Parameter(
        Mandatory = $false
    )]
    [string]$repo_url = "https://github.com/avengineers/SPL.git"
    , [Parameter(
        Mandatory = $false
    )]
    [switch]$skipInstall
    , [Parameter(
        Mandatory = $false
    )]
    [switch]$useCurrent ## use current directory as SPL
)

$splDir = "./build/spl-core"

if ($useCurrent) {
    Write-Information -Tags "Info:" -MessageData "Using current directory as SPL."
    $splDir = $PSScriptRoot
}
else {
    Write-Information -Tags "Info:" -MessageData "Cloning SPL version: $version from $repo_url"

    if (-Not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "'git' executable not found, please install it."
    }

    # This check works for tags as versions, only.
    # Use with care when you give a branch as version (no git pull here)
    if (Test-Path "$splDir/$version") {
        Write-Information -Tags "Info:" -MessageData "SPL-core version already set to $version, no update."
    }
    else {
        if (Test-Path "$splDir") {
            Remove-Item "$splDir" -Recurse -Force
        }
        git clone $repo_url --config advice.detachedHead=false --branch $version --depth 1 "$splDir"
        Out-File -FilePath "$splDir/$version"
    }
}

Push-Location "$splDir"

if ($skipInstall) {
    Write-Information -Tags "Info:" -MessageData "Skipping installation of dependencies."
}
else {
    . .\powershell\spl-variables.ps1
    . .\powershell\spl-functions.ps1

    if ($SPL_PROXY_HOST -and $SPL_PROXY_BYPASS_LIST) {
        Initialize-Proxy -ProxyHost $SPL_PROXY_HOST -NoProxy $SPL_PROXY_BYPASS_LIST
    }

    Install-Basic-Toolset
    Install-Toolset -FilePath "scoopfile.json"
}

Pop-Location #$splDir
