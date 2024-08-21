<#
.DESCRIPTION
    Wrapper for installing dependencies, running and testing the project

.Notes
On Windows, it may be required to enable this script by setting the execution
policy for the user. You can do this by issuing the following PowerShell command:

PS C:\> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

For more information on Execution Policies: 
https://go.microsoft.com/fwlink/?LinkID=135170
#>

param(
    [switch]$installMandatory ## install mandatory packages (e.g., CMake, Ninja, ...)
)

$ErrorActionPreference = "Stop"

# Needed on Jenkins, somehow the env var PATH is not updated automatically
# after tool installations by scoop
Function ReloadEnvVars () {
    $Env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

Function ScoopInstall ([string[]]$Packages) {
    Invoke-CommandLine -CommandLine "scoop install $Packages"
    ReloadEnvVars
}

Function Invoke-CommandLine {
    param (
        [string]$CommandLine,
        [bool]$StopAtError = $true,
        [bool]$Silent = $false
    )
    if (-Not $Silent) {
        Write-Host "Executing: $CommandLine"
    }
    Invoke-Expression $CommandLine
    if ($LASTEXITCODE -ne 0) {
        if ($StopAtError) {
            Write-Error "Command line call `"$CommandLine`" failed with exit code $LASTEXITCODE"
            exit 1
        }
        else {
            if (-Not $Silent) {
                Write-Host "Command line call `"$CommandLine`" failed with exit code $LASTEXITCODE, continuing ..."
            }
        }
    }
}

Push-Location $PSScriptRoot

Write-Output "Running in ${pwd}"

if ($installMandatory) {
    if (-Not (Get-Command scoop -errorAction SilentlyContinue)) {
        # Initial Scoop installation
        iwr get.scoop.sh -outfile 'install.ps1'
        if ((New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            & .\install.ps1 -RunAsAdmin
        } else {
            & .\install.ps1
        }
        ReloadEnvVars
    }

    # Necessary for 7zip installation, failed on Jenkins for unknown reason. See those issues:
    # https://github.com/ScoopInstaller/Scoop/issues/460
    # https://github.com/ScoopInstaller/Scoop/issues/4024
    ScoopInstall('lessmsi')
    Invoke-CommandLine -CommandLine "scoop config MSIEXTRACT_USE_LESSMSI $true"
    # Default installer tools, e.g., dark is required for python
    ScoopInstall('7zip', 'innounp', 'dark')
    Invoke-CommandLine -CommandLine "scoop bucket add extras" -StopAtError $false
    Invoke-CommandLine -CommandLine "scoop bucket add versions" -StopAtError $false

    Invoke-CommandLine -CommandLine "scoop update"
    ScoopInstall(Get-Content 'install-mandatory.list')
    $PipInstaller = "python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org"
    Invoke-CommandLine -CommandLine "$PipInstaller poetry"
    ReloadEnvVars
}

Invoke-CommandLine -CommandLine "poetry install"
Invoke-CommandLine -CommandLine "poetry run python -m pytest --verbose --capture=tee-sys"
Invoke-CommandLine -CommandLine "poetry build"
Invoke-CommandLine -CommandLine "poetry run make --directory doc html"

Pop-Location
