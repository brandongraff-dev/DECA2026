# Orbital Curbside offline demo server for Windows.
# Uses only what ships with Windows (PowerShell + .NET HttpListener): nothing to install,
# no internet, no admin rights. Serves this folder on http://localhost:8642 and opens the browser.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Split-Path -Parent $MyInvocation.MyCommand.Path))
if (-not $root.EndsWith([IO.Path]::DirectorySeparatorChar)) { $root += [IO.Path]::DirectorySeparatorChar }

$types = @{
  '.html' = 'text/html; charset=utf-8'; '.js' = 'text/javascript; charset=utf-8'; '.json' = 'application/json'
  '.css' = 'text/css'; '.jpg' = 'image/jpeg'; '.png' = 'image/png'; '.svg' = 'image/svg+xml'
  '.xml' = 'application/xml'; '.woff2' = 'font/woff2'; '.wasm' = 'application/wasm'; '.md' = 'text/plain'
  '.txt' = 'text/plain'; '.ico' = 'image/x-icon'
}

# Find a free port (8642 first, then a few spares).
$listener = $null
foreach ($port in 8642..8652) {
  $l = New-Object System.Net.HttpListener
  $l.Prefixes.Add("http://localhost:$port/")
  try { $l.Start(); $listener = $l; break } catch { $l.Close() }
}
if (-not $listener) { Write-Host 'Could not open a local port (8642-8652). Close other demo windows and try again.'; exit 1 }

$url = "http://localhost:$port/index.html"
Write-Host ''
Write-Host '  ORBITAL CURBSIDE - offline mission demo' -ForegroundColor DarkYellow
Write-Host "  Running at $url"
Write-Host '  Keep this window open during the demo. Close it to stop.'
Write-Host ''
if (-not $env:OC_NO_BROWSER) { Start-Process $url }

while ($listener.IsListening) {
  try {
    $ctx = $listener.GetContext()
    $res = $ctx.Response
    $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
    if ([string]::IsNullOrEmpty($rel)) { $rel = 'index.html' }
    $full = [IO.Path]::GetFullPath([IO.Path]::Combine($root, $rel))
    if ($full.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -and [IO.File]::Exists($full)) {
      $bytes = [IO.File]::ReadAllBytes($full)
      $ext = [IO.Path]::GetExtension($full).ToLowerInvariant()
      $res.ContentType = if ($types.ContainsKey($ext)) { $types[$ext] } else { 'application/octet-stream' }
      $res.Headers.Add('Cache-Control', 'no-cache')
      $res.ContentLength64 = $bytes.Length
      $res.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
      $res.StatusCode = 404
    }
    $res.Close()
  } catch {
    # A browser closing a connection early is normal; keep serving.
    try { $ctx.Response.Close() } catch {}
  }
}
