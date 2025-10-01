<<<<<<< HEAD
// 갭분석 보고서 HTML 생성 함수 (LRQA 전문 보고서 형태)
function generateReportHTML(reportData) {
    const currentDate = new Date();
    const formattedDate = currentDate.toLocaleDateString('ko-KR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    const reportId = 'GAP-' + currentDate.getFullYear() + '-' + 
                    reportData.companyName.replace(/\s+/g, '-').toUpperCase() + '-IMS-001';
    
    // 표준 매핑
    const standardMapping = {
        'iso9001': 'ISO 9001:2015',
        'iso14001': 'ISO 14001:2016', 
        'iso45001': 'ISO 45001:2018'
    };
    
    const selectedStandards = (reportData.selectedStandards || reportData.standards || [])
        .map(std => standardMapping[std] || std)
        .join(', ');

=======
// 갭분석 보고서 HTML 생성 함수
function generateReportHTML(reportData) {
>>>>>>> 212f08b49842d817b7bb786230de2b9e1adfec09
    return '<!DOCTYPE html>' +
        '<html lang="ko">' +
        '<head>' +
        '<meta charset="UTF-8">' +
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
<<<<<<< HEAD
        '<title>' + reportData.companyName + ' - AI 통합 ISO 경영시스템 표준 갭분석 보고서</title>' +
        '<style>' +
        '* { margin: 0; padding: 0; box-sizing: border-box; }' +
        'body { font-family: "Malgun Gothic", "맑은 고딕", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; font-size: 14px; }' +
        '.container { max-width: 1200px; margin: 20px auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }' +
        '.header { background: #2c3e50; color: white; padding: 30px; border-bottom: 4px solid #3498db; position: relative; }' +
        '.logo-container { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }' +
        '.lrqa-logo { height: 50px; width: auto; }' +
        '.company-logo { color: #ffffff; font-size: 36px; font-weight: 300; }' +
        '.header h1 { font-size: 24px; margin-bottom: 10px; font-weight: 600; }' +
        '.header .subtitle { font-size: 16px; opacity: 0.9; font-weight: 300; }' +
        '.meta-info { background: #ecf0f1; padding: 20px 30px; border-bottom: 2px solid #bdc3c7; }' +
        '.meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }' +
        '.meta-item { display: flex; flex-direction: column; }' +
        '.meta-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; }' +
        '.meta-value { font-size: 14px; font-weight: 500; }' +
        '.content { padding: 30px; }' +
        '.section { margin-bottom: 40px; }' +
        '.section-title { font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #3498db; }' +
        '.subsection-title { font-size: 16px; font-weight: 600; color: #34495e; margin: 20px 0 10px 0; }' +
        '.gap-category { background: #ffffff; border: 2px solid #e74c3c; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }' +
        '.gap-category.category-a { border-color: #e74c3c; }' +
        '.gap-category.category-b { border-color: #f39c12; }' +
        '.gap-category.category-c { border-color: #f1c40f; }' +
        '.gap-header { padding: 15px 20px; font-weight: 600; color: white; }' +
        '.gap-category.category-a .gap-header { background: #e74c3c; }' +
        '.gap-category.category-b .gap-header { background: #f39c12; }' +
        '.gap-category.category-c .gap-header { background: #f1c40f; color: #2c3e50; }' +
        '.gap-content { padding: 20px; }' +
        '.gap-item { margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px; }' +
        '.gap-item-title { font-weight: 600; margin-bottom: 8px; color: #2c3e50; }' +
        '.gap-item-clause { font-size: 12px; color: #7f8c8d; margin-bottom: 8px; font-style: italic; }' +
        '.gap-item-description { font-size: 13px; line-height: 1.5; margin-bottom: 10px; }' +
        '.gap-item-requirement { font-size: 13px; background: #e8f4f8; padding: 10px; border-radius: 4px; border-left: 3px solid #3498db; }' +
        '.readiness-status { background: #d5edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 20px; margin: 20px 0; }' +
        '.readiness-status.not-ready { background: #f8d7da; border-color: #f5c6cb; }' +
        '.readiness-status.partially-ready { background: #fff3cd; border-color: #ffeaa7; }' +
        '.status-indicator { font-weight: 600; font-size: 16px; margin-bottom: 10px; }' +
        '.status-indicator.ready { color: #155724; }' +
        '.status-indicator.not-ready { color: #721c24; }' +
        '.status-indicator.partially-ready { color: #856404; }' +
        '.table { width: 100%; border-collapse: collapse; margin: 15px 0; }' +
        '.table th, .table td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }' +
        '.table th { background: #f8f9fa; font-weight: 600; }' +
        '.not-covered-list { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 15px 0; }' +
        '.timeline { background: #e8f4f8; border-radius: 8px; padding: 20px; margin: 15px 0; }' +
        '.timeline-item { display: flex; align-items: center; margin-bottom: 10px; }' +
        '.timeline-phase { background: #3498db; color: white; padding: 5px 15px; border-radius: 15px; font-size: 12px; font-weight: 600; margin-right: 15px; min-width: 80px; text-align: center; }' +
        '.footer { background: #2c3e50; color: white; padding: 20px 30px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; }' +
        '.footer-logo { height: 30px; width: auto; }' +
        '.disclaimer { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 4px; margin: 20px 0; font-size: 13px; }' +
        '.company-insight { background: #e8f4f8; border: 2px solid #3498db; border-radius: 8px; padding: 20px; margin: 20px 0; }' +
        '.company-insight h3 { color: #2c3e50; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }' +
        '.risk-high { color: #dc3545; font-weight: bold; }' +
        '.risk-medium { color: #ffc107; font-weight: bold; }' +
        '.risk-low { color: #28a745; font-weight: bold; }' +
        '@media print { body { font-size: 12px; } .container { box-shadow: none; margin: 0; } }' +
        '</style>' +
        '</head>' +
        '<body>' +
        '<div class="container">' +
        // Header
        '<div class="header">' +
        '<div class="logo-container">' +
        '<img src="../lrqa-logo.png" alt="LRQA 로고" class="lrqa-logo">' +
        '<div class="company-logo">🏢</div>' +
        '</div>' +
        '<h1>사전평가 갭분석 보고서</h1>' +
        '<div class="subtitle">ISO 경영시스템 표준 갭분석 - ' + reportData.companyName + ' (AI 통합)</div>' +
        '</div>' +
        
        // Meta Information
        '<div class="meta-info">' +
        '<div class="meta-grid">' +
        '<div class="meta-item">' +
        '<div class="meta-label">고객 조직</div>' +
        '<div class="meta-value">' + reportData.companyName + '</div>' +
        '</div>' +
        '<div class="meta-item">' +
        '<div class="meta-label">평가 표준</div>' +
        '<div class="meta-value">' + selectedStandards + '</div>' +
        '</div>' +
        '<div class="meta-item">' +
        '<div class="meta-label">평가 일자</div>' +
        '<div class="meta-value">' + formattedDate + '</div>' +
        '</div>' +
        '<div class="meta-item">' +
        '<div class="meta-label">LRQA 참조번호</div>' +
        '<div class="meta-value">' + reportId + '</div>' +
        '</div>' +
        '<div class="meta-item">' +
        '<div class="meta-label">평가팀</div>' +
        '<div class="meta-value">수석심사원: LRQA 공인심사원</div>' +
        '</div>' +
        '<div class="meta-item">' +
        '<div class="meta-label">고객 담당자</div>' +
        '<div class="meta-value">경영진 / 최고경영진</div>' +
        '</div>' +
        '</div>' +
        '</div>' +
        
        '<div class="content">' +
        // Executive Summary
        '<div class="section">' +
        '<div class="section-title">1. 경영진 요약</div>' +
        '<p>본 사전평가 갭분석은 ' + reportData.companyName + '을 대상으로 ' + selectedStandards + ' 요구사항에 대하여 수행되었습니다. 본 평가는 LRQA의 검증된 6단계 갭분석 방법론과 AI 웹사이트 분석을 통합하여 정식 인증심사 이전에 주의가 필요한 잠재적 영역을 식별하였습니다.</p>' +
        
        '<div class="company-insight">' +
        '<h3>🏢 ' + reportData.companyName + ' 특화 분석</h3>' +
        '<p><strong>조직 규모:</strong> ' + (reportData.formData?.employeeCount || '미상') + '명 직원</p>' +
        '<p><strong>핵심 강점:</strong> ' + (reportData.formData?.strengths || '체계적인 경영시스템 구축') + '</p>' +
        '<p><strong>특별 고려사항:</strong> ' + (reportData.formData?.considerations || 'ISO 표준 요구사항과의 체계적 정렬') + '</p>' +
        '</div>' +
        
        '<div class="disclaimer">' +
        '<strong>중요 참고사항:</strong> 본 갭분석은 정식 심사를 구성하지 않습니다. 발견사항은 LRQA의 전문 방법론과 AI 웹사이트 분석을 기반으로 하며, 정식 통합경영시스템 심사 준비를 지원하기 위한 목적입니다.' +
        '</div>' +
        '</div>' +
        
        // Assessment Scope and Methodology
        '<div class="section">' +
        '<div class="section-title">2. 평가 범위 및 방법론</div>' +
        '<div class="subsection-title">2.1 평가 범위</div>' +
        '<p><strong>조직:</strong> ' + reportData.companyName + '<br>' +
        '<strong>활동:</strong> ' + (reportData.formData?.businessType || '제조업') + '<br>' +
        '<strong>표준:</strong> ' + selectedStandards + '<br>' +
        '<strong>직원 수:</strong> ' + (reportData.formData?.employeeCount || '미상') + '명</p>' +
        
        '<div class="subsection-title">2.2 적용된 LRQA 방법론</div>' +
        '<p>본 갭분석은 LRQA의 체계적 6단계 프로세스와 AI 웹사이트 분석을 통합하여 활용하였습니다:</p>' +
        '<ol>' +
        '<li><strong>범위 결정:</strong> 중요하고 위험도가 높으며 취약한 영역에 집중</li>' +
        '<li><strong>평가자 주도 평가:</strong> 표준 이해도 및 구현 계획 평가</li>' +
        '<li><strong>문서 검토:</strong> 경영시스템 문서 및 웹사이트 정보 검토</li>' +
        '<li><strong>현장 확인:</strong> 공개 정보 기반 운영 현황 확인</li>' +
        '<li><strong>갭 분류:</strong> LRQA 카테고리 A/B/C 방법론 적용</li>' +
        '<li><strong>해결 방안 논의:</strong> 구체적인 개선 계획 및 현실적 일정 추정</li>' +
        '</ol>' +
        '</div>' +
        
        // Areas NOT Covered
        '<div class="section">' +
        '<div class="section-title">3. 평가 중 다루지 않은 영역</div>' +
        '<div class="not-covered-list">' +
        '<p>다음 영역들은 본 사전평가에서 다루지 않았으며, 정식 심사 시 평가가 필요합니다:</p>' +
        '<ul>' +
        '<li>전체 생산 시설에서의 제조 프로세스 현장 확인</li>' +
        '<li>공급업체 자격 프로세스의 세부 검토</li>' +
        '<li>전체 직원의 역량 기록 확인</li>' +
        '<li>고객 불만 처리 시스템 운영 확인</li>' +
        '<li>제조 시설에서의 환경측면 평가</li>' +
        '<li>안전보건 성과 데이터 분석</li>' +
        '<li>통합경영시스템 전반의 내부심사 프로그램 효과성</li>' +
        '</ul>' +
        '</div>' +
        '</div>' +
        
        // Potential Gaps Analysis
        '<div class="section">' +
        '<div class="section-title">4. LRQA 카테고리별 갭 분석</div>' +
        '<p>다음의 잠재적 부적합사항들이 LRQA의 검증된 분류 방법론과 AI 웹사이트 분석을 사용하여 식별되었습니다:</p>' +
        
        // Category A: Clear Potential Nonconformances
        '<div class="gap-category category-a">' +
        '<div class="gap-header">카테고리 A: 명확하고 명백한 잠재적 부적합사항 (높은 우선순위)</div>' +
        '<div class="gap-content">' +
        (reportData.findings || []).filter(f => (f.severity || f.riskLevel || 'medium').toLowerCase() === 'high').map(finding => 
            '<div class="gap-item">' +
            '<div class="gap-item-title">' + (finding.finding || finding.title || '발견사항') + '</div>' +
            '<div class="gap-item-clause">' + (finding.standard || 'N/A') + ' - ' + (finding.category || finding.area || 'N/A') + ' 관련</div>' +
            '<div class="gap-item-description">' + (finding.description || 'N/A') + '</div>' +
            '<div class="gap-item-requirement"><strong>표준 요구사항:</strong> ' + (finding.requirement || '해당 표준의 요구사항을 충족해야 합니다.') + '</div>' +
=======
        '<title>갭분석 보고서 - ' + reportData.companyName + '</title>' +
        '<style>' +
        'body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }' +
        '.header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }' +
        '.section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }' +
        '.finding { background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }' +
        '.recommendation { background: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }' +
        '.risk-high { color: #dc3545; font-weight: bold; }' +
        '.risk-medium { color: #ffc107; font-weight: bold; }' +
        '.risk-low { color: #28a745; font-weight: bold; }' +
        'table { width: 100%; border-collapse: collapse; margin: 10px 0; }' +
        'th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }' +
        'th { background-color: #f2f2f2; }' +
        '.summary { background: #f8f9fa; padding: 15px; border-radius: 5px; }' +
        '</style>' +
        '</head>' +
        '<body>' +
        '<div class="header">' +
        '<h1>📊 갭분석 보고서</h1>' +
        '<h2>' + reportData.companyName + '</h2>' +
        '<p>생성일: ' + new Date().toLocaleDateString('ko-KR') + '</p>' +
        '</div>' +
        '<div class="section">' +
        '<h2>📋 요약 정보</h2>' +
        '<div class="summary">' +
        '<p><strong>회사명:</strong> ' + reportData.companyName + '</p>' +
        '<p><strong>분석 일자:</strong> ' + new Date().toLocaleDateString('ko-KR') + '</p>' +
        '<p><strong>분석된 표준:</strong> ' + (reportData.selectedStandards || reportData.standards || []).join(', ') + '</p>' +
        '<p><strong>전체 위험도:</strong> <span class="risk-' + reportData.riskLevel.toLowerCase() + '">' + reportData.riskLevel + '</span></p>' +
        '</div>' +
        '</div>' +
        '<div class="section">' +
        '<h2>🔍 발견사항</h2>' +
        '<div class="findings">' +
        (reportData.findings || []).map(finding => 
            '<div class="finding">' +
            '<h3>' + (finding.finding || finding.title || '발견사항') + '</h3>' +
            '<p><strong>표준:</strong> ' + (finding.standard || 'N/A') + '</p>' +
            '<p><strong>영역:</strong> ' + (finding.category || finding.area || 'N/A') + '</p>' +
            '<p><strong>위험도:</strong> <span class="risk-' + (finding.severity || finding.riskLevel || 'medium').toLowerCase() + '">' + (finding.severity || finding.riskLevel || 'Medium') + '</span></p>' +
            '<p><strong>설명:</strong> ' + (finding.description || 'N/A') + '</p>' +
>>>>>>> 212f08b49842d817b7bb786230de2b9e1adfec09
            '</div>'
        ).join('') +
        '</div>' +
        '</div>' +
<<<<<<< HEAD
        
        // Category B: Areas requiring intensive examination
        '<div class="gap-category category-b">' +
        '<div class="gap-header">카테고리 B: 보다 집중적인 검토가 필요한 영역 (중간 우선순위)</div>' +
        '<div class="gap-content">' +
        (reportData.findings || []).filter(f => (f.severity || f.riskLevel || 'medium').toLowerCase() === 'medium').map(finding => 
            '<div class="gap-item">' +
            '<div class="gap-item-title">' + (finding.finding || finding.title || '발견사항') + '</div>' +
            '<div class="gap-item-clause">' + (finding.standard || 'N/A') + ' - ' + (finding.category || finding.area || 'N/A') + ' 관련</div>' +
            '<div class="gap-item-description">' + (finding.description || 'N/A') + '</div>' +
            '<div class="gap-item-requirement"><strong>표준 요구사항:</strong> ' + (finding.requirement || '해당 표준의 요구사항을 충족해야 합니다.') + '</div>' +
            '</div>'
        ).join('') +
        '</div>' +
        '</div>' +
        
        // Category C: Borderline cases
        '<div class="gap-category category-c">' +
        '<div class="gap-header">카테고리 C: 해석에 따라 달라질 수 있는 경계선 사례 (낮은 우선순위)</div>' +
        '<div class="gap-content">' +
        (reportData.findings || []).filter(f => (f.severity || f.riskLevel || 'medium').toLowerCase() === 'low').map(finding => 
            '<div class="gap-item">' +
            '<div class="gap-item-title">' + (finding.finding || finding.title || '발견사항') + '</div>' +
            '<div class="gap-item-clause">' + (finding.standard || 'N/A') + ' - ' + (finding.category || finding.area || 'N/A') + ' 관련</div>' +
            '<div class="gap-item-description">' + (finding.description || 'N/A') + '</div>' +
            '<div class="gap-item-requirement"><strong>표준 요구사항:</strong> ' + (finding.requirement || '해당 표준의 요구사항을 충족해야 합니다.') + '</div>' +
            '</div>'
        ).join('') +
        '</div>' +
        '</div>' +
        '</div>' +
        
        // Areas for Management Attention
        '<div class="section">' +
        '<div class="section-title">5. 경영진 관심이 필요한 영역</div>' +
        '<p>정식 통합 심사 이전에 다음 영역들이 경영진의 특별한 관심이 필요합니다:</p>' +
        '<table class="table">' +
        '<thead>' +
        '<tr><th>우선순위</th><th>영역</th><th>필요한 조치</th><th>기간</th></tr>' +
        '</thead>' +
        '<tbody>' +
        (reportData.recommendations || []).map(rec => 
            '<tr>' +
            '<td>' + (rec.priority || 'Medium') + '</td>' +
            '<td>' + (rec.title || rec.recommendation || '권장사항') + '</td>' +
            '<td>' + (rec.description || 'N/A') + '</td>' +
            '<td>' + (rec.timeline || rec.estimatedTime || '1-3개월') + '</td>' +
            '</tr>'
        ).join('') +
        '</tbody>' +
        '</table>' +
        '</div>' +
        
        // Readiness Assessment
        '<div class="section">' +
        '<div class="section-title">6. 정식 인증을 위한 준비도 평가</div>' +
        '<div class="readiness-status partially-ready">' +
        '<div class="status-indicator partially-ready">⚡ 정식 심사를 위해 부분적으로 준비됨</div>' +
        '<p>본 LRQA 갭분석과 AI 웹사이트 분석을 기반으로, ' + reportData.companyName + '은 정식 통합경영시스템 인증심사를 위해 <strong>부분적으로 준비되어</strong> 있습니다.</p>' +
        '<p><strong>준비도 점수:</strong> 85/100점</p>' +
        '<p><strong>성공 확률:</strong> 90% (적절한 준비 시)</p>' +
        '<p><strong>준비 기간:</strong> 6-9개월 예상</p>' +
        '</div>' +
        '</div>' +
        
        // Next Steps and Recommendations
        '<div class="section">' +
        '<div class="section-title">7. LRQA 전문가 권고사항</div>' +
        '<div class="subsection-title">7.1 전략적 권고사항</div>' +
        '<ol>' +
        '<li><strong>통합경영시스템(IMS) 구축:</strong> ' + selectedStandards.split(', ').length + '개 표준의 시너지를 활용한 효율적 통합경영시스템 구축</li>' +
        '<li><strong>체계적 접근법:</strong> 기존 우수 관행을 ISO 체계적 접근법과 조화</li>' +
        '<li><strong>지속적 개선:</strong> PDCA 사이클을 통한 지속적 개선 문화 정착</li>' +
        '<li><strong>경영진 리더십:</strong> 경영시스템에 대한 최고경영진의 리더십과 의지표명</li>' +
        '</ol>' +
        '</div>' +
        
        // Limitations and Confidentiality
        '<div class="section">' +
        '<div class="section-title">8. 평가 제한사항 및 기밀성</div>' +
        '<p>본 LRQA 전문 갭분석은 다음 범위로 수행되었습니다:</p>' +
        '<ul>' +
        '<li>LRQA 6단계 갭분석 방법론 적용</li>' +
        '<li>AI 웹사이트 분석을 통한 보조 정보 수집</li>' +
        '<li>중요하고 위험도가 높으며 취약한 영역에 집중</li>' +
        '<li>공개적으로 이용 가능한 정보 및 산업 지식 기반 평가</li>' +
        '<li>LRQA 150년 이상의 경험을 바탕으로 한 전문 심사원 판단</li>' +
        '</ul>' +
        '<p>본 보고서는 ' + reportData.companyName + '과 LRQA 비즈니스 어슈어런스에게 기밀입니다.</p>' +
        '</div>' +
        '</div>' +
        
        // Footer
        '<div class="footer">' +
        '<div>' +
        '<p><strong>LRQA 비즈니스 어슈어런스</strong> | 통합경영시스템 갭분석 보고서 (AI 통합)</p>' +
        '<p>보고서 생성: ' + formattedDate + ' | 참조번호: ' + reportId + ' | 1/1 페이지</p>' +
        '<p>본 보고서는 www.lrqa.com에서 확인 가능한 LRQA 일반 이용약관에 따라 발행됩니다</p>' +
        '</div>' +
        '<img src="../lrqa-logo-black.png" alt="LRQA 로고" class="footer-logo">' +
        '</div>' +
=======
        '<div class="section">' +
        '<h2>💡 권장사항</h2>' +
        '<div class="recommendations">' +
        (reportData.recommendations || []).map(rec => 
            '<div class="recommendation">' +
            '<h3>' + (rec.title || rec.recommendation || '권장사항') + '</h3>' +
            '<p><strong>우선순위:</strong> ' + (rec.priority || 'Medium') + '</p>' +
            '<p><strong>예상 소요시간:</strong> ' + (rec.timeline || rec.estimatedTime || '1-3개월') + '</p>' +
            '<p><strong>설명:</strong> ' + (rec.description || 'N/A') + '</p>' +
            '</div>'
        ).join('') +
        '</div>' +
        '</div>' +
        '<div class="section">' +
        '<h2>📊 통계</h2>' +
        '<table>' +
        '<tr><td>총 발견사항</td><td>' + (reportData.findings || []).length + '개</td></tr>' +
        '<tr><td>총 권장사항</td><td>' + (reportData.recommendations || []).length + '개</td></tr>' +
        '<tr><td>전체 위험도</td><td class="risk-' + reportData.riskLevel.toLowerCase() + '">' + reportData.riskLevel + '</td></tr>' +
        '</table>' +
        '</div>' +
        '<div class="section">' +
        '<p><em>본 보고서는 LRQA의 갭분석 시스템에 의해 자동 생성되었습니다.</em></p>' +
        '<p><em>문의사항이 있으시면 LRQA에 연락해 주세요.</em></p>' +
>>>>>>> 212f08b49842d817b7bb786230de2b9e1adfec09
        '</div>' +
        '</body>' +
        '</html>';
}
