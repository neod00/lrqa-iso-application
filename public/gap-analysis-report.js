// 갭분석 보고서 HTML 생성 함수
function generateReportHTML(reportData) {
    return '<!DOCTYPE html>' +
        '<html lang="ko">' +
        '<head>' +
        '<meta charset="UTF-8">' +
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">' +
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
            '</div>'
        ).join('') +
        '</div>' +
        '</div>' +
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
        '</div>' +
        '</body>' +
        '</html>';
}
