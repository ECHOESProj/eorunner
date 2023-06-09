$env:PYTHONPATH = "${PSScriptRoot}/..";
& $PSScriptRoot/../.venv/Scripts/Activate.ps1

Set-Location -Path $PSScriptRoot/..
python -m app $args --module=ndvi --module=ndwi --module=water_bodies --module=water_bodies_occurence --module=water_in_wetlands_index --module=vpp-total-productivity-tprod --module=corine_land_cover --log=batch2 --cleanup
python -m app $args --module=ndvi --module=ndwi --module=water_bodies --module=water_bodies_occurence --module=water_in_wetlands_index --module=vpp-total-productivity-tprod --module=corine_land_cover --log=batch2 --backdate --cleanup

Remove-Item Env:\PYTHONPATH
deactivate
