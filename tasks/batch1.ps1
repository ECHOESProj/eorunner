$env:PYTHONPATH = "${PSScriptRoot}/..";
& $PSScriptRoot/../.venv/Scripts/Activate.ps1

Set-Location -Path $PSScriptRoot/..
python -m app $args --module=sar_false_color_visualization --module=barren_soil --module=ndmi_special --module=true_color --module=^global_surface --log=batch1 --cleanup
python -m app $args --module=sar_false_color_visualization --module=barren_soil --module=ndmi_special --module=true_color --module=^global_surface --log=batch1 --backdate --cleanup

Remove-Item Env:\PYTHONPATH
deactivate
