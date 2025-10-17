# PowerShell script to set up Grafana datasource and import dashboard

Write-Host "======================================"  -ForegroundColor Cyan
Write-Host "Grafana Setup Script"  -ForegroundColor Cyan
Write-Host "======================================"  -ForegroundColor Cyan
Write-Host ""

# Wait for Grafana to be ready
Write-Host "Checking if Grafana is ready..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$grafanaReady = $false

while (-not $grafanaReady -and $retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $grafanaReady = $true
            Write-Host "✓ Grafana is ready!" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "  Waiting for Grafana... ($retryCount/$maxRetries)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if (-not $grafanaReady) {
    Write-Host "✗ Grafana is not responding. Please check if it's running." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create InfluxDB datasource
Write-Host "Creating InfluxDB datasource..." -ForegroundColor Yellow

$datasourceConfig = @{
    name = "InfluxDB"
    type = "influxdb"
    access = "proxy"
    url = "http://influxdb:8086"
    jsonData = @{
        version = "Flux"
        organization = "gpu-monitoring"
        defaultBucket = "gpu-metrics"
        tlsSkipVerify = $true
    }
    secureJsonData = @{
        token = "my-super-secret-auth-token"
    }
} | ConvertTo-Json -Depth 10

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources" `
        -Method Post `
        -Headers $headers `
        -Body $datasourceConfig `
        -Credential (New-Object System.Management.Automation.PSCredential("admin", (ConvertTo-SecureString "admin" -AsPlainText -Force))) `
        -ErrorAction SilentlyContinue

    Write-Host "✓ InfluxDB datasource created successfully!" -ForegroundColor Green
    $datasourceUid = $response.datasource.uid
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "  InfluxDB datasource already exists" -ForegroundColor Gray

        # Get existing datasource
        try {
            $datasources = Invoke-RestMethod -Uri "http://localhost:3000/api/datasources" `
                -Method Get `
                -Credential (New-Object System.Management.Automation.PSCredential("admin", (ConvertTo-SecureString "admin" -AsPlainText -Force)))

            $influxDs = $datasources | Where-Object { $_.type -eq "influxdb" } | Select-Object -First 1
            if ($influxDs) {
                $datasourceUid = $influxDs.uid
                Write-Host "✓ Using existing InfluxDB datasource (UID: $datasourceUid)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  Could not retrieve datasource UID" -ForegroundColor Yellow
        }
    } else {
        Write-Host "✗ Failed to create datasource: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""

# Import dashboard
Write-Host "Importing dashboard..." -ForegroundColor Yellow

$dashboardPath = Join-Path $PSScriptRoot "dashboard\gpu-monitoring-dashboard.json"

if (Test-Path $dashboardPath) {
    try {
        $dashboardJson = Get-Content $dashboardPath -Raw | ConvertFrom-Json

        # Update datasource UID if we have one
        if ($datasourceUid) {
            # Update all panel datasources
            foreach ($panel in $dashboardJson.panels) {
                if ($panel.datasource) {
                    $panel.datasource.uid = $datasourceUid
                }
                if ($panel.targets) {
                    foreach ($target in $panel.targets) {
                        if ($target.datasource) {
                            $target.datasource.uid = $datasourceUid
                        }
                    }
                }
            }
        }

        $importPayload = @{
            dashboard = $dashboardJson
            overwrite = $true
            inputs = @()
        } | ConvertTo-Json -Depth 20

        $response = Invoke-RestMethod -Uri "http://localhost:3000/api/dashboards/db" `
            -Method Post `
            -Headers $headers `
            -Body $importPayload `
            -Credential (New-Object System.Management.Automation.PSCredential("admin", (ConvertTo-SecureString "admin" -AsPlainText -Force)))

        Write-Host "✓ Dashboard imported successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "======================================"  -ForegroundColor Cyan
        Write-Host "Dashboard URL:"  -ForegroundColor Cyan
        Write-Host "http://localhost:3000$($response.url)" -ForegroundColor White
        Write-Host "======================================"  -ForegroundColor Cyan
        Write-Host ""

        # Open dashboard in browser
        Start-Process "http://localhost:3000$($response.url)"

    } catch {
        Write-Host "✗ Failed to import dashboard: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "You can import manually:" -ForegroundColor Yellow
        Write-Host "1. Go to http://localhost:3000" -ForegroundColor White
        Write-Host "2. Login with admin/admin" -ForegroundColor White
        Write-Host "3. Dashboards > New > Import" -ForegroundColor White
        Write-Host "4. Upload: $dashboardPath" -ForegroundColor White
    }
} else {
    Write-Host "✗ Dashboard JSON file not found at: $dashboardPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Data is flowing:" -ForegroundColor Cyan
Write-Host "  Producer: Sending metrics to Kafka" -ForegroundColor White
Write-Host "  Consumer: Writing to InfluxDB" -ForegroundColor White
Write-Host "  Grafana:  Visualizing real-time data" -ForegroundColor White
Write-Host ""
