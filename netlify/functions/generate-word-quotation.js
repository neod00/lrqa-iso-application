const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, HeadingLevel, BorderStyle } = require('docx');

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리 (CORS preflight)
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed',
                message: 'POST 요청만 허용됩니다.'
            })
        };
    }

    try {
        console.log('=== 견적서 생성 시작 ===');
        
        const requestBody = JSON.parse(event.body);
        const { timestamp, applicationData } = requestBody;
        
        if (!timestamp || !applicationData) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    success: false, 
                    message: 'Missing required data: timestamp and applicationData' 
                })
            };
        }

        console.log('견적서 데이터:', applicationData);

        // 견적서 데이터 변환
        const quotationData = convertApplicationToQuotationData(applicationData);
        
        // LRQA 스타일 Word 문서 생성
        const buffer = await createLRQAQuotationDocument(quotationData);
        
        // Base64로 인코딩
        const base64File = buffer.toString('base64');

        console.log('=== 견적서 생성 완료 ===');

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                success: true,
                message: '견적서가 성공적으로 생성되었습니다.',
                filename: `LRQA_견적서_${applicationData['법인명(국문)'] || 'Unknown'}_${new Date().toISOString().split('T')[0]}.docx`,
                fileData: base64File
            })
        };

    } catch (error) {
        console.error('=== 견적서 생성 오류 ===');
        console.error('Error:', error);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '견적서 생성 중 오류가 발생했습니다.',
                details: error.message
            })
        };
    }
};

/**
 * 신청서 데이터를 견적서 생성용 데이터로 변환
 */
function convertApplicationToQuotationData(applicationData) {
    // 표준 정보 추출
    const standards = [];
    if (applicationData['ISO표준']) {
        const isoStandards = applicationData['ISO표준'];
        if (isoStandards.includes('ISO 9001') || isoStandards.includes('ISO9001')) {
            standards.push('ISO 9001');
        }
        if (isoStandards.includes('ISO 14001') || isoStandards.includes('ISO14001')) {
            standards.push('ISO 14001');
        }
        if (isoStandards.includes('ISO 45001') || isoStandards.includes('ISO45001')) {
            standards.push('ISO 45001');
        }
    }

    // 기본값 설정
    if (standards.length === 0) {
        standards.push('ISO 9001');
    }

    // 직원 수
    const totalEmployees = parseInt(applicationData['총직원수']) || 30;
    
    // 견적 계산 (간단한 로직)
    const baseDays = calculateAuditDays(totalEmployees, standards.length);
    const dayRate = 1400000; // 1 manday 단가
    const subtotal = baseDays * dayRate;
    const vat = subtotal * 0.1;
    const totalCost = subtotal + vat;

    return {
        // 회사 정보
        companyName: applicationData['법인명(국문)'] || '알 수 없음',
        companyNameEn: applicationData['법인명(영문)'] || applicationData['법인명(국문)'] || 'Unknown',
        address: applicationData['본사주소'] || '서울시 강남구',
        contactName: applicationData['담당자명'] || '알 수 없음',
        contactEmail: applicationData['담당자이메일'] || 'unknown@example.com',
        contactPhone: applicationData['담당자전화'] || '010-0000-0000',
        
        // 견적 정보
        quotationNumber: `LRQA-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-${Math.floor(Math.random() * 10000).toString().padStart(4, '0')}`,
        quotationDate: new Date().toLocaleDateString('ko-KR'),
        validUntil: new Date(Date.now() + 90*24*60*60*1000).toLocaleDateString('ko-KR'),
        
        // 표준 정보
        standards: standards,
        standardsText: standards.join(', '),
        
        // 직원 정보
        totalEmployees: totalEmployees,
        
        // 견적 상세
        auditDays: baseDays,
        dayRate: dayRate,
        subtotal: subtotal,
        vat: vat,
        totalCost: totalCost,
        
        // 기타
        isIntegrated: applicationData['다중표준시스템'] === '예',
        remoteAudit: applicationData['원격심사'] === '예'
    };
}

/**
 * 심사일수 계산 (간단한 로직)
 */
function calculateAuditDays(employees, standardCount) {
    let baseDays = 0;
    
    // 직원 수에 따른 기본 일수
    if (employees <= 10) {
        baseDays = 1.5;
    } else if (employees <= 50) {
        baseDays = 2.0;
    } else if (employees <= 100) {
        baseDays = 2.5;
    } else if (employees <= 250) {
        baseDays = 3.0;
    } else if (employees <= 500) {
        baseDays = 3.5;
    } else {
        baseDays = 4.0;
    }
    
    // 표준 수에 따른 가중치
    const standardMultiplier = Math.min(standardCount * 0.3, 0.6); // 최대 60% 증가
    baseDays = baseDays * (1 + standardMultiplier);
    
    return Math.round(baseDays * 10) / 10; // 소수점 첫째자리까지
}

/**
 * LRQA 스타일 Word 문서 생성
 */
async function createLRQAQuotationDocument(data) {
    const doc = new Document({
        sections: [{
            properties: {},
            children: [
                // 헤더 - LRQA 로고 및 제목
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "LRQA Korea",
                            bold: true,
                            size: 32,
                            color: "1f4e79"
                        })
                    ],
                    alignment: AlignmentType.CENTER,
                    spacing: { after: 400 }
                }),
                
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "ISO 인증심사 견적서",
                            bold: true,
                            size: 28,
                            color: "1f4e79"
                        })
                    ],
                    alignment: AlignmentType.CENTER,
                    spacing: { after: 600 }
                }),
                
                // 견적서 정보 테이블
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "견적서 번호", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.quotationNumber })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "작성일", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.quotationDate })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "유효기간", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.validUntil })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "작성자", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "LRQA Korea" })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({ children: [new TextRun({ text: "" })] }), // 빈 줄
                
                // 고객사 정보
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "고객사 정보",
                            bold: true,
                            size: 24,
                            color: "1f4e79"
                        })
                    ],
                    spacing: { before: 400, after: 200 }
                }),
                
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "회사명", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.companyName })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "영문명", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.companyNameEn })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "주소", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.address })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "담당자", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.contactName })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                })
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "연락처", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.contactPhone })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "이메일", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.contactEmail })] })],
                                    width: { size: 30, type: WidthType.PERCENTAGE }
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({ children: [new TextRun({ text: "" })] }), // 빈 줄
                
                // 인증 범위
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "인증 범위",
                            bold: true,
                            size: 24,
                            color: "1f4e79"
                        })
                    ],
                    spacing: { before: 400, after: 200 }
                }),
                
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "신청 표준", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: data.standardsText })] })],
                                    width: { size: 80, type: WidthType.PERCENTAGE }
                                })
                            ]
                        },
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "총 직원 수", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.totalEmployees}명` })] })],
                                    width: { size: 80, type: WidthType.PERCENTAGE }
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({ children: [new TextRun({ text: "" })] }), // 빈 줄
                
                // 견적 상세
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "견적 상세",
                            bold: true,
                            size: 24,
                            color: "1f4e79"
                        })
                    ],
                    spacing: { before: 400, after: 200 }
                }),
                
                new Table({
                    width: { size: 100, type: WidthType.PERCENTAGE },
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "항목", bold: true })] })],
                                    width: { size: 40, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "수량", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "단가", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "금액", bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                })
                            ]
                        },
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "ISO 인증심사 (Stage 1 + Stage 2)" })] })],
                                    width: { size: 40, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.auditDays}일` })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.dayRate.toLocaleString()}원` })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.subtotal.toLocaleString()}원` })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                })
                            ]
                        },
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "소계" })] })],
                                    width: { size: 40, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.subtotal.toLocaleString()}원` })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                })
                            ]
                        },
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "VAT (10%)" })] })],
                                    width: { size: 40, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.vat.toLocaleString()}원` })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                })
                            ]
                        },
                        new TableRow({
                            children: [
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "총 견적 금액", bold: true })] })],
                                    width: { size: 40, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: "" })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                }),
                                new TableCell({
                                    children: [new Paragraph({ children: [new TextRun({ text: `${data.totalCost.toLocaleString()}원`, bold: true })] })],
                                    width: { size: 20, type: WidthType.PERCENTAGE }
                                })
                            ]
                        })
                    ]
                }),
                
                new Paragraph({ children: [new TextRun({ text: "" })] }), // 빈 줄
                
                // 주의사항
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "주의사항",
                            bold: true,
                            size: 20,
                            color: "1f4e79"
                        })
                    ],
                    spacing: { before: 400, after: 200 }
                }),
                
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "• 본 견적서는 유효기간 내에만 유효합니다.",
                            size: 20
                        })
                    ],
                    spacing: { after: 100 }
                }),
                
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "• 견적서 승인 후 계약서 체결이 필요합니다.",
                            size: 20
                        })
                    ],
                    spacing: { after: 100 }
                }),
                
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "• 심사 일정은 계약 체결 후 협의하여 결정됩니다.",
                            size: 20
                        })
                    ],
                    spacing: { after: 100 }
                }),
                
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "• 문의사항이 있으시면 언제든지 연락주시기 바랍니다.",
                            size: 20
                        })
                    ],
                    spacing: { after: 200 }
                }),
                
                // 푸터
                new Paragraph({
                    children: [
                        new TextRun({
                            text: "LRQA Korea | 사업개발본부 | Tel: 02-1234-5678 | Email: info@lrqa.co.kr",
                            size: 16,
                            color: "666666"
                        })
                    ],
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 400 }
                })
            ]
        }]
    });
    
    return await Packer.toBuffer(doc);
}
