param([string]$Tool = 'list_documents', [string]$Arguments = '{}', [string]$CodeFile)
$ErrorActionPreference = 'Stop'
$toolArgs = ConvertFrom-Json -AsHashtable $Arguments
if ($CodeFile) {
    $Tool = 'execute_code'
    $resolved = (Resolve-Path -LiteralPath $CodeFile).Path.Replace('\','/')
    $pythonPath = ConvertTo-Json -InputObject $resolved -Compress
    $toolArgs = @{code=("__file__ = $pythonPath`n" + (Get-Content -Raw -LiteralPath $CodeFile))}
}
$request = @{jsonrpc='2.0'; id=1; method='tools/call'; params=@{name=$Tool; arguments=$toolArgs}} | ConvertTo-Json -Depth 30
$response = Invoke-RestMethod -Uri 'http://127.0.0.1:3000/mcp' -Method Post -ContentType application/json -Body $request -TimeoutSec 240
if ($response.error) { throw ($response.error | ConvertTo-Json -Depth 10) }
$response.result | ConvertTo-Json -Depth 25
if ($response.result.isError) { exit 1 }
