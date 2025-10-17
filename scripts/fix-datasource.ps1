# Fix Grafana InfluxDB Datasource

Write-Host "Checking InfluxDB datasource configuration..." -ForegroundColor Cyan

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))
}

# Get all datasources
try {
    $datasources = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources" -Method Get -Headers $headers

    Write-Host ""
    Write-Host "Found datasources:" -ForegroundColor Yellow
    foreach ($ds in $datasources) {
        Write-Host "  - Name: $($ds.name), Type: $($ds.type), UID: $($ds.uid)" -ForegroundColor White
    }

    # Find InfluxDB datasource
    $influxDs = $datasources | Where-Object { $_.type -eq "influxdb" } | Select-Object -First 1

    if ($influxDs) {
        Write-Host ""
        Write-Host "Testing InfluxDB connection..." -ForegroundColor Cyan

        # Test datasource
        $testResult = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources/uid/$($influxDs.uid)/health" -Method Get -Headers $headers -ErrorAction SilentlyContinue

        Write-Host "Connection test result:" -ForegroundColor Yellow
        Write-Host ($testResult | ConvertTo-Json) -ForegroundColor White
    }

} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Manual Fix Steps:" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. In Grafana, click the gear icon (Settings) on the left"
Write-Host "2. Click 'Data Sources'"
Write-Host "3. Click on 'InfluxDB' (if it exists) OR click 'Add data source'"
Write-Host "4. Configure:"
Write-Host "   Name: InfluxDB"
Write-Host "   Query Language: Flux"
Write-Host "   URL: http://influxdb:8086"
Write-Host "   Organization: gpu-monitoring"
Write-Host "   Token: my-super-secret-auth-token"
Write-Host "   Default Bucket: gpu-metrics"
Write-Host "5. Click 'Save & Test' - should show green success"
Write-Host "6. Go back to your dashboard - data should appear!"
Write-Host ""
