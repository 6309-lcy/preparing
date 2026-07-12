# Copy app/ -> docs/ for GitHub Pages (Settings → Pages → /docs)
$root = Split-Path -Parent $PSScriptRoot
$src = Join-Path $root "app"
$dst = Join-Path $root "docs"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse
Write-Host "Copied app/ -> docs/"
Write-Host "Next: git add docs; git commit; git push"
Write-Host "Then GitHub repo Settings → Pages → Deploy from branch → /docs"
