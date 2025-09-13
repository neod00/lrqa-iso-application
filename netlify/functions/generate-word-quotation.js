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
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ success: false, error: 'Method not allowed' })
        };
    }

    try {
        const requestBody = JSON.parse(event.body);
        const { quotationData, adminEmail } = requestBody;

        console.log('견적서 생성 시작:', quotationData);

        const companyName = quotationData.companyName || '회사명 없음';
        const contactName = quotationData.contactName || '담당자 없음';
        const contactEmail = quotationData.contactEmail || '이메일 없음';
        const totalEmployees = quotationData.totalEmployees || 0;
        const siteCount = quotationData.siteCount || 1;
        const isoStandards = quotationData.isoStandards || [];

        const isoStandardNames = {
            'iso9001': 'ISO 9001 (품질경영시스템)',
            'iso14001': 'ISO 14001 (환경경영시스템)',
            'iso45001': 'ISO 45001 (직업안전보건경영시스템)'
        };

        const selectedStandards = isoStandards.map(std => isoStandardNames[std] || std).join(', ');

        let baseDays = 0;
        if (totalEmployees <= 10) baseDays = 1;
        else if (totalEmployees <= 50) baseDays = 2;
        else if (totalEmployees <= 100) baseDays = 3;
        else if (totalEmployees <= 500) baseDays = 4;
        else baseDays = 5;

        const additionalDays = (siteCount - 1) * 0.5;
        const totalDays = Math.ceil(baseDays + additionalDays);
        const dailyRate = 1450000;
        const totalFee = totalDays * dailyRate;
        const additionalExpenses = Math.round(totalFee * 0.1);
        const grandTotal = totalFee + additionalExpenses;

        const doc = new Document({
            sections: [{
                properties: {},
                children: [
                    new Paragraph({
                        children: [new TextRun({ text: "LRQA ISO 인증심사 견적서", bold: true, size: 32 })],
                        alignment: AlignmentType.CENTER,
                        spacing: { after: 400 }
                    }),
                    new Paragraph({
                        children: [new TextRun({ text: "견적 요청 기업 정보", bold: true, size: 24 })],
                        spacing: { before: 200, after: 200 }
                    }),
                    new Table({
                        width: { size: 100, type: WidthType.PERCENTAGE },
                        rows: [
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: "회사명", bold: true })] })],
                                        width: { size: 30, type: WidthType.PERCENTAGE },
                                        shading: { fill: "F2F2F2" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: companyName })] })],
                                        width: { size: 70, type: WidthType.PERCENTAGE }
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: "담당자", bold: true })] })],
                                        shading: { fill: "F2F2F2" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: contactName })] })]
                                    })
                                ]
                            }),
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: "총 직원 수", bold: true })] })],
                                        shading: { fill: "F2F2F2" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: totalEmployees.toString() + "명" })] })]
                                    })
                                ]
                            })
                        ]
                    }),
                    new Paragraph({
                        children: [new TextRun({ text: "견적서 상세", bold: true, size: 24 })],
                        spacing: { before: 400, after: 200 }
                    }),
                    new Table({
                        width: { size: 100, type: WidthType.PERCENTAGE },
                        rows: [
                            new TableRow({
                                children: [
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: "총 견적 금액", bold: true })] })],
                                        shading: { fill: "FFF2CC" }
                                    }),
                                    new TableCell({
                                        children: [new Paragraph({ children: [new TextRun({ text: grandTotal.toLocaleString() + "원", bold: true })] })],
                                        shading: { fill: "FFF2CC" }
                                    })
                                ]
                            })
                        ]
                    })
                ]
            }]
        });

        const buffer = await Packer.toBuffer(doc);
        console.log('Word 견적서 생성 완료');

        return {
            statusCode: 200,
            headers: {
                ...headers,
                'Content-Disposition': `attachment; filename="quotation_${quotationData.id || 'quotation'}.docx"`,
                'Content-Length': buffer.length.toString()
            },
            body: buffer.toString('base64'),
            isBase64Encoded: true
        };

    } catch (error) {
        console.error('Error generating quotation:', error);
        return {
            statusCode: 500,
            headers: { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' },
            body: JSON.stringify({
                success: false,
                error: 'Internal server error',
                message: '견적서 생성 중 오류가 발생했습니다.'
            })
        };
    }
};
