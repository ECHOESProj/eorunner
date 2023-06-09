# Prompt to run as administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))  
{  
  $arguments = "& '" +$myinvocation.mycommand.definition + "'"
  Start-Process powershell -Verb runAs -ArgumentList $arguments
  Break
}

$venv_path = "${PSScriptRoot}/.venv"

# remove previous virtual environment
Remove-Item $venv_path -Recurse -Force -ErrorAction Ignore

# create virtual environment with specific Python version and activate
py -3.6 -m venv $venv_path
& $venv_path/Scripts/Activate.ps1

# cwd so requirements.txt can be found
Set-Location -Path $PSScriptRoot

# Upgrade pip and install packages
python -m pip install --upgrade pip
pip install -r requirements.txt
