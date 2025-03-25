Start-Process -NoNewWindow -FilePath "dotnet" -ArgumentList "run --project=CSVOracle\CSVOracle.Server\"
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m flask --app .\CSVOracle\CSVOracle.PythonScripts\llm_server run"
