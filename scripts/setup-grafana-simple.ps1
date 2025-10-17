# Simple Grafana Setup Script

Write-Host "======================================"
Write-Host "Grafana Setup Script"
Write-Host "======================================"
Write-Host ""

# Wait for Grafana
Write-Host "Checking if Grafana is ready..."
Start-Sleep -Seconds 5

# Create datasource
Write-Host "Creating InfluxDB datasource..."

$datasourceConfig = @"
{
  "name": "InfluxDB",
  "type": "influxdb",
  "access": "proxy",
  "url": "http://influxdb:8086",
  "jsonData": {
    "version": "Flux",
    "organization": "gpu-monitoring",
    "defaultBucket": "gpu-metrics",
    "tlsSkipVerify": true
  },
  "secureJsonData": {
    "token": "my-super-secret-auth-token"
  }
}
"@

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources" `
        -Method Post `
        -Headers $headers `
        -Body $datasourceConfig `
        -ErrorAction Stop

    Write-Host "SUCCESS: InfluxDB datasource created!" -ForegroundColor Green
    $datasourceUid = $response.datasource.uid
    Write-Host "Datasource UID: $datasourceUid"
} catch {
    Write-Host "Note: Datasource may already exist (this is OK)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================"
Write-Host "Next steps:"
Write-Host "======================================"
Write-Host "1. Open http://localhost:3000"
Write-Host "2. Login: admin / admin"
Write-Host "3. Click Dashboards (left sidebar)"
Write-Host "4. Click 'New' then 'Import'"
Write-Host "5. Upload file: dashboard\gpu-monitoring-dashboard.json"
Write-Host "6. Select InfluxDB datasource"
Write-Host "7. Click Import"
Write-Host ""
Write-Host "Your dashboard will be live with 11 panels!"
Write-Host ""

# Open Grafana
Start-Process "http://localhost:3000"
