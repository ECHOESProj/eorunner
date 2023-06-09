$env:PYTHONPATH = "${PSScriptRoot}/..";
& $PSScriptRoot/../.venv/Scripts/Activate.ps1

Set-Location -Path $PSScriptRoot/..
python -m app $args

Remove-Item Env:\PYTHONPATH
deactivate
