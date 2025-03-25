Start-Process -NoNewWindow -FilePath "dotnet" -ArgumentList "watch --project=CSVOracle\CSVOracle.Server\"
Start-Process -FilePath "python" -ArgumentList "-m flask --app .\CSVOracle\CSVOracle.PythonScripts\llm_server run --debug"
