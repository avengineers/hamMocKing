pushd %~dp0
powershell -ExecutionPolicy Bypass -File .\build.ps1 %* || exit /b 1
popd
