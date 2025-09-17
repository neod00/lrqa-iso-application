#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# admin.html 파일 읽기
with open('public/admin.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 견적서 버튼 CSS 스타일 추가
quotation_css = """
        .action-btn.quote {
            background-color: #10b981;
            color: white;
        }
        
        .action-btn.quote:hover {
            background-color: #059669;
        }
"""

# CSS 스타일 섹션에 견적서 버튼 스타일 추가
content = content.replace(
    '.action-btn:hover {',
    quotation_css + '\n        .action-btn:hover {'
)

# 신청서 목록 테이블에 견적서 버튼 추가
quotation_button = """
                            <button class="action-btn quote" onclick="generateQuotation('${app['신청시']}')">견적서</button>
"""

# 기존 액션 버튼들 뒤에 견적서 버튼 추가
content = content.replace(
    '                            <button class="action-btn edit" onclick="editApplication(\'${app[\'신청시\']}\')">수정</button>',
    '                            <button class="action-btn edit" onclick="editApplication(\'${app[\'신청시\']}\')">수정</button>\n' + quotation_button
)

# 견적서 생성 함수 추가
quotation_function = """
        // 견적서 생성 함수
        async function generateQuotation(timestamp) {
            if (!isAuthenticated) return;
            
            try {
                showMessage('견적서를 생성 중입니다...', 'info');
                
                // 신청서 데이터 가져오기
                const response = await fetch('/.netlify/functions/get-applications');
                const result = await response.json();
                
                if (!result.success) {
                    showMessage('신청서 데이터를 불러올 수 없습니다.', 'error');
                    return;
                }
                
                const application = result.data.applications.find(app => app['신청시'] === timestamp);
                if (!application) {
                    showMessage('신청서를 찾을 수 없습니다.', 'error');
                    return;
                }

                // Python 백엔드 API 호출 (로컬 서버용)
                const quotationResponse = await fetch('https://lrqa-iso-application-1ysvzpqdd-dal-kims-projects.vercel.app/generate-quotation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        timestamp: timestamp,
                        applicationData: application
                    })
                });
                
                if (quotationResponse.ok) {
                    // Word 파일 다운로드
                    const blob = await quotationResponse.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `LRQA_견적서_${application['법인명(국문)']}_${new Date().toISOString().split('T')[0]}.docx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    
                    showMessage('견적서가 성공적으로 생성되었습니다!', 'success');
                } else {
                    const errorData = await quotationResponse.json();
                    showMessage(errorData.message || '견적서 생성 중 오류가 발생했습니다.', 'error');
                }
                
            } catch (error) {
                console.error('Error generating quotation:', error);
                showMessage('견적서 생성 중 오류가 발생했습니다.', 'error');
            }
        }
"""

# JavaScript 섹션 끝에 견적서 생성 함수 추가
content = content.replace(
    '</script>',
    quotation_function + '\n    </script>'
)

# 파일 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("견적서 생성 기능 추가 완료")
