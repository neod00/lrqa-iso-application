/**
 * JavaScript 기반 Word 견적서 생성 Netlify Function
 * LRQA 견적서 템플릿을 기반으로 Word 문서 생성
 */

const { 
    Document, 
    Packer, 
    Paragraph, 
    TextRun, 
    Table, 
    TableRow, 
    TableCell, 
    WidthType, 
    AlignmentType, 
    BorderStyle,
    HeadingLevel,
    ShadingType
} = require('docx');

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

    // POST 요청만 처리
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: 'Method not allowed' 
            })
        };
    }

    try {
        console.log('=== JavaScript Word 견적서 생성 시작 ===');
        
        // 요청 데이터 파싱
        const requestData = JSON.parse(event.body);
        console.log('받은 데이터:', Object.keys(requestData));

        // LRQA 견적서 Word 문서 생성
        const doc = new Document({
            sections: [{
                properties: {},
                children: [
                    // 헤더 섹션
                    createHeader(requestData),
                    
                    // 회사 정보 섹션
                    createCompanyInfo(requestData),
                    
                    // 견적 상세 테이블
                    createQuotationTable(requestData),
                    
                    // 가정 및 근거 섹션
                    createAssumptionsSection(requestData),
                    
                    // 푸터 섹션
                    createFooter(requestData)
                ]
            }]
        });

        // Word 파일 생성
        const buffer = await Packer.toBuffer(doc);
        
        console.log('Word 견적서 생성 완료');
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'Content-Disposition': `attachment; filename="LRQA_견적서_${requestData.client_name || 'Test'}_${new Date().toISOString().split('T')[0]}.docx"`
            },
            body: buffer.toString('base64'),
            isBase64Encoded: true
        };

    } catch (error) {
        console.error('Word 견적서 생성 오류:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                success: false,
                error: error.message,
                message: 'Word 견적서 생성 중 오류가 발생했습니다.'
            })
        };
    }
};

// 헤더 생성 함수
function createHeader(data) {
    return new Paragraph({
        children: [
            new TextRun({
                text: "LRQA 견적서",
                bold: true,
                size: 32,
                color: "2c3e50"
            })
        ],
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 }
    });
}

// 회사 정보 섹션 생성
function createCompanyInfo(data) {
    return new Table({
        width: {
            size: 100,
            type: WidthType.PERCENTAGE
        },
        rows: [
            new TableRow({
                children: [
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "견적서 번호:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.quotation_number || `LRQA-${new Date().toISOString().split('T')[0]}` })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "작성일:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.quotation_date || new Date().toLocaleDateString('ko-KR') })]
                        })]
                    })
                ]
            }),
            new TableRow({
                children: [
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "고객사:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.client_name || "" })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "담당자:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.contact_person || "" })]
                        })]
                    })
                ]
            }),
            new TableRow({
                children: [
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "주소:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.client_address || "" })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "연락처:", bold: true })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "F8F9FA"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: data.contact_phone || "" })]
                        })]
                    })
                ]
            })
        ]
    });
}

// 견적 상세 테이블 생성
function createQuotationTable(data) {
    const quotationDetails = data.quotation_details || [];
    
    return new Table({
        width: {
            size: 100,
            type: WidthType.PERCENTAGE
        },
        rows: [
            // 헤더 행
            new TableRow({
                children: [
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "표준", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "ENP", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "Stage1", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "Stage2", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "Surveillance", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "소계", bold: true, color: "FFFFFF" })]
                        })],
                        shading: {
                            type: ShadingType.SOLID,
                            color: "2c3e50"
                        }
                    })
                ]
            }),
            // 데이터 행들
            ...quotationDetails.map((detail, index) => 
                new TableRow({
                    children: [
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: detail.standard_name || detail.standard })]
                            })]
                        }),
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: `${detail.enp}명` })]
                            })]
                        }),
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: `${detail.stage1_days}일` })]
                            })]
                        }),
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: `${detail.stage2_days}일` })]
                            })]
                        }),
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: `${detail.surveillance_days}일` })]
                            })]
                        }),
                        new TableCell({
                            children: [new Paragraph({
                                children: [new TextRun({ text: `${detail.total_days}일` })]
                            })]
                        })
                    ],
                    shading: index % 2 === 0 ? {
                        type: ShadingType.SOLID,
                        color: "F8F9FA"
                    } : undefined
                })
            ),
            // 총계 행
            new TableRow({
                children: [
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: "총계", bold: true })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: `${data.total_employees || 0}명` })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: `${data.stage1_days || 0}일` })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: `${data.stage2_days || 0}일` })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: `${data.surveillance_days || 0}일` })]
                        })]
                    }),
                    new TableCell({
                        children: [new Paragraph({
                            children: [new TextRun({ text: `${data.total_audit_days || 0}일`, bold: true })]
                        })]
                    })
                ],
                shading: {
                    type: ShadingType.SOLID,
                    color: "E8F5E8"
                }
            })
        ]
    });
}

// 가정 및 근거 섹션 생성
function createAssumptionsSection(data) {
    const assumptions = data.assumptions || [
        "심사는 정상적인 업무시간 내에 진행됩니다.",
        "고객사는 심사에 필요한 모든 자료를 사전에 준비합니다.",
        "심사원의 안전한 현장 접근이 보장됩니다."
    ];
    const justification = data.justification || [
        "ADJ v2.2 기준에 따른 심사일수 계산",
        "직원 수 및 업종별 복잡도 고려",
        "통합심사 시 할인 적용"
    ];
    
    return new Paragraph({
        children: [
            new TextRun({
                text: "가정 사항:",
                bold: true,
                size: 24,
                color: "2c3e50"
            }),
            new TextRun({
                text: "\n" + assumptions.map(a => `• ${a}`).join('\n'),
                size: 20
            }),
            new TextRun({
                text: "\n\n근거 사항:",
                bold: true,
                size: 24,
                color: "2c3e50"
            }),
            new TextRun({
                text: "\n" + justification.map(j => `• ${j}`).join('\n'),
                size: 20
            })
        ],
        spacing: { before: 400, after: 400 }
    });
}

// 푸터 섹션 생성
function createFooter(data) {
    return new Paragraph({
        children: [
            new TextRun({
                text: `작성자: ${data.prepared_by || "LRQA Korea"}`,
                size: 20
            }),
            new TextRun({
                text: `\n소속: ${data.prepared_title || "사업개발본부"}`,
                size: 20
            }),
            new TextRun({
                text: `\n작성일: ${data.created_at || new Date().toISOString()}`,
                size: 20
            })
        ],
        alignment: AlignmentType.RIGHT,
        spacing: { before: 400 }
    });
}
