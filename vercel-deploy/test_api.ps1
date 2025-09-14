# PowerShell API 테스트 스크립트
# Vercel 로컬 개발 서버에서 API 기능을 테스트합니다.

Write-Host "🚀 Vercel API 테스트 시작" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Yellow

# 로컬 개발 서버 URL
$BaseUrl = "http://localhost:3000"

# 서버 시작 대기
Write-Host "⏳ 로컬 개발 서버 시작 대기 중..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# 신청서 제출 API 테스트
Write-Host "`n🧪 신청서 제출 API 테스트 시작..." -ForegroundColor Cyan

$TestData = @{
    company_name = "테스트제조업체"
    company_name_en = "Test Manufacturing Co."
    contact_name = "홍길동"
    contact_email = "hong@test.com"
    contact_phone = "010-1234-5678"
    address = "서울시 강남구 테헤란로 123"
    standards = @("ISO 9001", "ISO 14001")
    total_employees = 50
    site_count = 1
    part_time_count = 5
    contractor_count = 10
    shift_workers = 8
    is_integrated = $true
    shared_management_system = $true
    common_processes = $true
    stage1 = $true
    stage2 = $true
    surveillance = $true
    remote_audit_ratio = 0.2
}

$JsonData = $TestData | ConvertTo-Json -Depth 3

try {
    $Response = Invoke-RestMethod -Uri "$BaseUrl/api/submit-application" -Method POST -Body $JsonData -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ 신청서 제출 API 테스트 성공!" -ForegroundColor Green
    Write-Host "응답: $($Response | ConvertTo-Json -Depth 3)" -ForegroundColor White
    $ApplicationResult = $Response
} catch {
    Write-Host "❌ 신청서 제출 API 테스트 실패: $($_.Exception.Message)" -ForegroundColor Red
    $ApplicationResult = $null
}

# 견적서 생성 API 테스트
Write-Host "`n🧪 견적서 생성 API 테스트 시작..." -ForegroundColor Cyan

$QuotationData = @{
    company_name = "테스트제조업체"
    company_name_en = "Test Manufacturing Co."
    contact_name = "홍길동"
    contact_email = "hong@test.com"
    contact_phone = "010-1234-5678"
    address = "서울시 강남구 테헤란로 123"
    standards = @("ISO 9001", "ISO 14001")
    total_employees = 50
    sites = @(@{
        name = "본사"
        address = "서울시 강남구 테헤란로 123"
        total_headcount = 50
        part_time_count = 5
        contractor_count = 10
        shift_workers = 8
        standards = @("ISO 9001", "ISO 14001")
    })
    integration = @{
        is_integrated = $true
        shared_management_system = $true
        common_processes = $true
        same_audit_team = $false
    }
    options = @{
        stage1 = $true
        stage2 = $true
        surveillance = $true
        recert = $false
        remote_audit_ratio = 0.2
        day_rate = 1300000
        vat_rate = 0.1
    }
}

$QuotationJsonData = $QuotationData | ConvertTo-Json -Depth 4

try {
    $Response = Invoke-RestMethod -Uri "$BaseUrl/api/create-quotation" -Method POST -Body $QuotationJsonData -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ 견적서 생성 API 테스트 성공!" -ForegroundColor Green
    Write-Host "응답: $($Response | ConvertTo-Json -Depth 3)" -ForegroundColor White
    $QuotationResult = $Response
} catch {
    Write-Host "❌ 견적서 생성 API 테스트 실패: $($_.Exception.Message)" -ForegroundColor Red
    $QuotationResult = $null
}

# 이메일 전송 API 테스트
if ($QuotationResult -and $QuotationResult.success) {
    Write-Host "`n🧪 이메일 전송 API 테스트 시작..." -ForegroundColor Cyan
    
    $EmailData = @{
        recipient_email = "hong@test.com"
        quotation = $QuotationResult.quotation
    }
    
    $EmailJsonData = $EmailData | ConvertTo-Json -Depth 3
    
    try {
        $Response = Invoke-RestMethod -Uri "$BaseUrl/api/send-email" -Method POST -Body $EmailJsonData -ContentType "application/json" -TimeoutSec 30
        Write-Host "✅ 이메일 전송 API 테스트 성공!" -ForegroundColor Green
        Write-Host "응답: $($Response | ConvertTo-Json -Depth 3)" -ForegroundColor White
    } catch {
        Write-Host "❌ 이메일 전송 API 테스트 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n==================================================" -ForegroundColor Yellow
Write-Host "🏁 API 테스트 완료" -ForegroundColor Green

# 결과 요약
if ($ApplicationResult -and $QuotationResult) {
    Write-Host "✅ 모든 API 테스트가 성공적으로 완료되었습니다!" -ForegroundColor Green
    if ($QuotationResult.quotation) {
        Write-Host "📊 견적 금액: ₩$($QuotationResult.quotation.total_cost.ToString('N0'))" -ForegroundColor Cyan
        Write-Host "📅 총 심사일수: $($QuotationResult.quotation.total_audit_days)일" -ForegroundColor Cyan
    }
} else {
    Write-Host "❌ 일부 API 테스트가 실패했습니다." -ForegroundColor Red
}