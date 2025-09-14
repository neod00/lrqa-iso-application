/**
 * LRQA 견적서 생성 Netlify Function
 * 견적서 데이터를 저장하고 Word 문서를 생성하는 서버사이드 함수
 */

const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, WidthType, Table, TableRow, TableCell, BorderStyle } = require('docx');
const { GoogleSpreadsheet } = require('google-spreadsheet');
const { JWT } = require('google-auth-library');

exports.handler = async (event, context) => {
    // CORS 헤더 설정
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS 요청 처리
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        // POST 요청만 처리
        if (event.httpMethod !== 'POST') {
            return {
                statusCode: 405,
                headers,
                body: JSON.stringify({ success: false, message: 'Method not allowed' })
            };
        }

        const quotationData = JSON.parse(event.body);

        // 견적서 데이터 검증
        if (!quotationData || !quotationData.companyName) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ success: false, message: '견적서 데이터가 올바르지 않습니다.' })
            };
        }

        // Google Sheets 연결 설정
        const serviceAccountAuth = new JWT({
            email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
            key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
            scopes: ['https://www.googleapis.com/auth/spreadsheets']
        });

        const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID, serviceAccountAuth);
        await doc.loadInfo();

        // 견적서 시트 찾기 또는 생성
        let quotationSheet;
        try {
            quotationSheet = doc.sheetsByTitle['견적서'];
        } catch (error) {
            // 견적서 시트가 없으면 생성
            quotationSheet = await doc.addSheet({
                title: '견적서',
                headerValues: [
                    '견적서ID',
                    '신청서ID',
                    '회사명',
                    '담당자',
                    '연락처',
                    '이메일',
                    '직원수',
                    '사업장수',
                    '업종',
                    '복잡도',
                    '심사유형',
                    '총심사일수',
                    '심사비',
                    '제경비',
                    '총견적금액',
                    '생성일시',
                    '상태'
                ]
            });
        }

        // 견적서 데이터 추가
        const row = {
            '견적서ID': quotationData.id,
            '신청서ID': quotationData.applicationId,
            '회사명': quotationData.companyName,
            '담당자': quotationData.contactPerson,
            '연락처': quotationData.contactPhone,
            '이메일': quotationData.contactEmail,
            '직원수': quotationData.employeeCount,
            '사업장수': quotationData.siteCount,
            '업종': quotationData.industryType,
            '복잡도': quotationData.complexity,
            '심사유형': quotationData.auditType,
            '총심사일수': quotationData.totalDays,
            '심사비': quotationData.auditFee,
            '제경비': quotationData.expenses,
            '총견적금액': quotationData.totalAmount,
            '생성일시': quotationData.createdDate,
            '상태': quotationData.status
        };

        await quotationSheet.addRow(row);

        // Word 문서 생성
        const doc = new Document({
            sections: [{
                properties: {},
                children: [
                    // 헤더
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "LRQA Korea",
                                bold: true,
                                size: 32,
                                color: "2c3e50"
                            })
                        ],
                        alignment: AlignmentType.CENTER,
                        spacing: { after: 400 }
                    }),
                    
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "ISO 9001 인증심사 견적서",
                                bold: true,
                                size: 24,
                                color: "3498db"
                            })
                        ],
                        alignment: AlignmentType.CENTER,
                        spacing: { after: 600 }
                    }),

                    // 회사 정보
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "견적 정보",
                                bold: true,
                                size: 20,
                                color: "2c3e50"
                            })
                        ],
                        heading: HeadingLevel.HEADING_1,
                        spacing: { before: 400, after: 200 }
                    }),

                    // 견적 테이블
                    new Table({
                        width: {
                            size: 100,
                            type: WidthType.PERCENTAGE,
                        },
                        rows: [
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("회사명")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(quotationData.companyName)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("담당자")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(quotationData.contactPerson)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("연락처")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(quotationData.contactPhone)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("직원 수")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(`${quotationData.employeeCount}명`)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("사업장 수")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(`${quotationData.siteCount}개소`)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            })
                        ],
                        borders: {
                            top: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            bottom: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            left: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            right: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            insideVertical: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" }
                        }
                    }),

                    new Paragraph({ text: "", spacing: { after: 400 } }),

                    // 견적 금액
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "견적 금액",
                                bold: true,
                                size: 20,
                                color: "2c3e50"
                            })
                        ],
                        heading: HeadingLevel.HEADING_1,
                        spacing: { before: 400, after: 200 }
                    }),

                    // 견적 테이블
                    new Table({
                        width: {
                            size: 100,
                            type: WidthType.PERCENTAGE,
                        },
                        rows: [
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("심사일수")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(`${quotationData.totalDays}일`)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("심사비 (일당 1,450,000원)")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(`${quotationData.auditFee.toLocaleString()}원`)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("제경비 (10%)")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "f8f9fa" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph(`${quotationData.expenses.toLocaleString()}원`)],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph("총 견적 금액")],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "e8f5e8" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph({
                                            children: [
                                                new TextRun({
                                                    text: `${quotationData.totalAmount.toLocaleString()}원`,
                                                    bold: true,
                                                    color: "e74c3c"
                                                })
                                            ]
                                        })],
                                        width: { size: 70, type: WidthType.PERCENTAGE },
                                        shading: { fill: "e8f5e8" }
                                    })
                                ]
                            })
                        ],
                        borders: {
                            top: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            bottom: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            left: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            right: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" },
                            insideVertical: { style: BorderStyle.SINGLE, size: 1, color: "cccccc" }
                        }
                    }),

                    new Paragraph({ text: "", spacing: { after: 400 } }),

                    // 하단 정보
                    new Paragraph({
                        children: [
                            new TextRun({
                                text: "본 견적서는 ADJ_v.2.2 기준에 따라 산정되었습니다.",
                                size: 12,
                                color: "6c757d"
                            })
                        ],
                        alignment: AlignmentType.CENTER,
                        spacing: { before: 400 }
                    }),

                    new Paragraph({
                        children: [
                            new TextRun({
                                text: `견적일: ${new Date(quotationData.createdDate).toLocaleDateString('ko-KR')}`,
                                size: 12,
                                color: "6c757d"
                            })
                        ],
                        alignment: AlignmentType.CENTER
                    })
                ]
            }]
        });

        // 문서를 Buffer로 변환
        const buffer = await Packer.toBuffer(doc);
        
        // 파일명 생성
        const fileName = `LRQA_ISO9001_quotation_${quotationData.companyName}_${new Date().toISOString().split('T')[0]}.docx`;

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'Content-Disposition': `attachment; filename="${fileName}"`,
                'Content-Length': buffer.length.toString()
            },
            body: buffer.toString('base64'),
            isBase64Encoded: true
        };

    } catch (error) {
        console.error('견적서 생성 오류:', error);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                message: '견적서 생성 중 오류가 발생했습니다.',
                error: error.message
            })
        };
    }
};
