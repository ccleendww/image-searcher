# Git 上传脚本 - 上传到 GitHub
# 用法: .\上传.ps1

$repoUrl = "https://github.com/ccleendww/image-searcher.git"
$currentDir = Get-Location

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始上传项目到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已初始化 Git 仓库
if (-not (Test-Path ".git")) {
    Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git 仓库已初始化" -ForegroundColor Green
    Write-Host ""
}

# 配置 Git 用户（如果需要）
$userName = git config user.name
$userEmail = git config user.email

if (-not $userName) {
    Write-Host "配置 Git 用户名..." -ForegroundColor Yellow
    $name = Read-Host "请输入 Git 用户名"
    git config user.name $name
    Write-Host "✓ 用户名已设置: $name" -ForegroundColor Green
}

if (-not $userEmail) {
    Write-Host "配置 Git 邮箱..." -ForegroundColor Yellow
    $email = Read-Host "请输入 Git 邮箱"
    git config user.email $email
    Write-Host "✓ 邮箱已设置: $email" -ForegroundColor Green
}

Write-Host ""

# 检查远程仓库
$remoteExists = git remote | Where-Object { $_ -eq "origin" }

if (-not $remoteExists) {
    Write-Host "添加远程仓库..." -ForegroundColor Yellow
    git remote add origin $repoUrl
    Write-Host "✓ 远程仓库已添加: $repoUrl" -ForegroundColor Green
}
else {
    Write-Host "远程仓库已存在，获取远程地址..." -ForegroundColor Yellow
    $currentUrl = git remote get-url origin
    Write-Host "当前远程地址: $currentUrl" -ForegroundColor Cyan
    
    if ($currentUrl -ne $repoUrl) {
        Write-Host "更新远程仓库地址..." -ForegroundColor Yellow
        git remote set-url origin $repoUrl
        Write-Host "✓ 远程仓库已更新" -ForegroundColor Green
    }
}

Write-Host ""

# 查看当前状态
Write-Host "当前 Git 状态:" -ForegroundColor Yellow
git status --short

Write-Host ""

# 添加所有文件
Write-Host "添加所有更改的文件..." -ForegroundColor Yellow
git add .
Write-Host "✓ 文件已添加" -ForegroundColor Green

Write-Host ""

# 获取提交信息
$commitMessage = Read-Host "请输入提交信息 (默认: Update project)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update project"
}

# 提交
Write-Host "提交更改..." -ForegroundColor Yellow
git commit -m $commitMessage
Write-Host "✓ 提交完成" -ForegroundColor Green

Write-Host ""

# 获取当前分支名
$branch = git rev-parse --abbrev-ref HEAD

# 推送到远程
Write-Host "推送到远程仓库 ($branch 分支)..." -ForegroundColor Yellow
git push -u origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 推送成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "项目已成功上传到 GitHub" -ForegroundColor Cyan
    Write-Host "仓库地址: $repoUrl" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}
else {
    Write-Host "✗ 推送失败，请检查网络连接或认证信息" -ForegroundColor Red
    Write-Host "如遇到认证问题，请使用以下命令配置 SSH 或 token" -ForegroundColor Yellow
    Write-Host "SSH: git remote set-url origin git@github.com:ccleendww/image-searcher.git" -ForegroundColor Gray
}

Write-Host ""
