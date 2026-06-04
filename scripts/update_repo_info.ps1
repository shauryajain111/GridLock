# Sets topics, description, and homepage for Gridlock-Hackathon-2.0 via GitHub API.
# Requires: $env:GITHUB_TOKEN with repo scope (or gh auth token)

$owner = "shauryajain111"
$repo = "Gridlock-Hackathon-2.0"
$full = "$owner/$repo"

$token = $env:GITHUB_TOKEN
if (-not $token) {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) { $token = gh auth token 2>$null }
}
if (-not $token) {
    Write-Error "Set GITHUB_TOKEN or run: gh auth login"
    exit 1
}

$headers = @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$description = "Perfect-score traffic demand prediction for Flipkart Gridlock Hackathon 2.0 — spatiotemporal lookup (R² = 1.0)."
$homepage = "https://www.hackerearth.com/challenges/competitive/gridlock-hackathon-20/"
$topics = @(
    "machine-learning",
    "hackathon",
    "pandas",
    "traffic-prediction",
    "hackerearth",
    "flipkart"
)

# Patch repo description + homepage
$patchBody = @{ description = $description; homepage = $homepage } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.github.com/repos/$full" -Method PATCH -Headers $headers -Body $patchBody -ContentType "application/json"
Write-Host "Updated description and homepage."

# Replace topics (names only; GitHub API)
$topicBody = @{ names = $topics } | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.github.com/repos/$full/topics" -Method PUT -Headers @{
    Authorization = "Bearer $token"
    Accept        = "application/vnd.github.mercy-preview+json"
    "X-GitHub-Api-Version" = "2022-11-28"
} -Body $topicBody -ContentType "application/json"
Write-Host "Topics set: $($topics -join ', ')"

Write-Host "Done. Pin the repo manually: https://github.com/$owner?tab=repositories"
