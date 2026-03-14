if ($args -contains "-reset") {
    Remove-Item game_data* -ErrorAction SilentlyContinue
    Remove-Item game_data -ErrorAction SilentlyContinue
    Write-Host "Dev Mode: Data reset triggered."
}
se_env\Scripts\Activate
python main.pyw
deactivate

