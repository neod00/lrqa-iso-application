/**
 * LRQA 견적서 워드 문서 생성기
 * .docx 형식으로 견적서 생성
 */
class WordDocumentGenerator {
    constructor() {
        this.defaultTemplate = null;
    }

    async generateQuotationDocument(quotation, formData, type = 'formal') {
        try {
            const template = await this.loadTemplate();
            
            // 견적서 번호 생성
            const quotationNumber = type === 'draft' 
                ? `DRAFT-${this.generateQuotationNumber()}`
                : this.generateQuotationNumber();
            
            const doc = await this.createDocument(quotation, formData, quotationNumber, type);
            return doc;
        } catch (error) {
            console.error('문서 생성 실패:', error);
            throw error;
        }
    }

    async createDocument(quotation, formData, quotationNumber, type) {
        // DocxGen 라이브러리 확인
        if (typeof PizZip === 'undefined' || typeof Docxtemplater === 'undefined') {
            throw new Error('DocxGen 라이브러리가 로드되지 않았습니다.');
        }

        try {
            // 기본 템플릿 생성
            const template = this.createDefaultTemplate(type);
            
            // 데이터 매핑
            const processedTemplate = this.mapDataToTemplate(template, quotation, formData, quotationNumber, type);
            
            // 문서 생성
            const zip = new PizZip();
            zip.file('word/document.xml', processedTemplate);
            
            // 필수 파일들 추가
            zip.file('[Content_Types].xml', this.getContentTypesXML());
            zip.file('_rels/.rels', this.getRelsXML());
            zip.file('word/_rels/document.xml.rels', this.getDocumentRelsXML());
            
            return zip.generate({ type: 'blob' });
        } catch (error) {
            console.error('문서 생성 중 오류:', error);
            throw error;
        }
    }

    async loadTemplate() {
        // 외부 템플릿 파일이 있으면 로드, 없으면 기본 템플릿 사용
        try {
            const response = await fetch('quotation-system/templates/quotation-template.docx');
            if (response.ok) {
                const arrayBuffer = await response.arrayBuffer();
                this.defaultTemplate = new PizZip(arrayBuffer);
                return this.defaultTemplate;
            }
        } catch (error) {
            console.log('외부 템플릿 로드 실패, 기본 템플릿 사용:', error);
        }
        
        return null;
    }

    createDefaultTemplate(type) {
        // LRQA 담당자용 정식 견적서 템플릿
        if (type === 'formal') {
            return `
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                    <w:body>
                        <!-- LRQA 로고 및 헤더 -->
                        <w:p>
                            <w:pPr>
                                <w:jc w:val="center"/>
                            </w:pPr>
                            <w:r>
                                <w:t>LRQA</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:pPr>
                                <w:jc w:val="center"/>
                            </w:pPr>
                            <w:r>
                                <w:t>ISO 인증 심사 견적서</w:t>
                            </w:r>
                        </w:p>
                        
                        <!-- 견적서 정보 -->
                        <w:p>
                            <w:r>
                                <w:t>견적서 번호: {quotationNumber}</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>견적 일자: {quotationDate}</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>회사명: {companyName}</w:t>
                            </w:r>
                        </w:p>
                        
                        <!-- 견적 상세 내역 -->
                        <w:p>
                            <w:r>
                                <w:t>견적 상세 내역</w:t>
                            </w:r>
                        </w:p>
                        
                        {standardBreakdown}
                        
                        <!-- 추가 서비스 -->
                        {additionalServices}
                        
                        <!-- 할인 내역 -->
                        {discounts}
                        
                        <!-- 총 견적 금액 -->
                        <w:p>
                            <w:r>
                                <w:t>총 견적 금액: ₩{totalAmount}</w:t>
                            </w:r>
                        </w:p>
                        
                        <!-- 견적 참고사항 -->
                        <w:p>
                            <w:r>
                                <w:t>견적 참고사항</w:t>
                            </w:r>
                        </w:p>
                        
                        {quotationNotes}
                        
                        <!-- 유효기간 및 조건 -->
                        <w:p>
                            <w:r>
                                <w:t>유효기간: 30일</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>이 견적서는 LRQA 담당자 검토 후 승인됩니다.</w:t>
                            </w:r>
                        </w:p>
                    </w:body>
                </w:document>
            `;
        } else {
            // 사용자용 초안 템플릿 (간단한 형태)
            return `
                <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                    <w:body>
                        <w:p>
                            <w:pPr>
                                <w:jc w:val="center"/>
                            </w:pPr>
                            <w:r>
                                <w:t>견적서 초안 (참고용)</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>⚠️ 이 견적서는 참고용이며, 정식 견적서가 아닙니다.</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>견적서 번호: {quotationNumber}</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>회사명: {companyName}</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>총 견적 금액: ₩{totalAmount}</w:t>
                            </w:r>
                        </w:p>
                        
                        <w:p>
                            <w:r>
                                <w:t>정식 견적서는 LRQA 담당자 검토 후 발송됩니다.</w:t>
                            </w:r>
                        </w:p>
                    </w:body>
                </w:document>
            `;
        }
    }

    generateQuotationTableRows(quotation) {
        let rows = '';
        
        if (quotation.standardBreakdown) {
            quotation.standardBreakdown.forEach(item => {
                rows += `
                    <w:tr>
                        <w:tc>
                            <w:p>
                                <w:r>
                                    <w:t>${item.standard}</w:t>
                                </w:r>
                            </w:p>
                        </w:tc>
                        <w:tc>
                            <w:p>
                                <w:r>
                                    <w:t>₩${item.amount.toLocaleString()}</w:t>
                                </w:r>
                            </w:p>
                        </w:tc>
                    </w:tr>
                `;
            });
        }
        
        return rows;
    }

    generateDiscountSection(quotation) {
        if (!quotation.discounts || quotation.discounts.length === 0) {
            return '<w:p><w:r><w:t>적용된 할인이 없습니다.</w:t></w:r></w:p>';
        }
        
        let discountHTML = '<w:p><w:r><w:t>할인 내역:</w:t></w:r></w:p>';
        
        quotation.discounts.forEach(discount => {
            discountHTML += `
                <w:p>
                    <w:r>
                        <w:t>${discount.name}: -₩${discount.amount.toLocaleString()}</w:t>
                    </w:r>
                </w:p>
            `;
        });
        
        return discountHTML;
    }

    generateNotesSection(quotation) {
        if (!quotation.notes || quotation.notes.length === 0) {
            return '<w:p><w:r><w:t>특별한 참고사항이 없습니다.</w:t></w:r></w:p>';
        }
        
        let notesHTML = '';
        quotation.notes.forEach(note => {
            notesHTML += `
                <w:p>
                    <w:r>
                        <w:t>• ${note}</w:t>
                    </w:r>
                </w:p>
            `;
        });
        
        return notesHTML;
    }

    mapDataToTemplate(template, quotation, formData, quotationNumber, type) {
        // 기본 데이터 매핑
        let processedTemplate = template
            .replace(/{quotationNumber}/g, quotationNumber)
            .replace(/{quotationDate}/g, new Date().toLocaleDateString('ko-KR'))
            .replace(/{companyName}/g, formData.companyName || '미입력')
            .replace(/{totalAmount}/g, quotation.totalAmount.toLocaleString())
            .replace(/{standardBreakdown}/g, this.generateQuotationTableRows(quotation))
            .replace(/{additionalServices}/g, this.generateAdditionalServicesSection(quotation))
            .replace(/{discounts}/g, this.generateDiscountSection(quotation))
            .replace(/{quotationNotes}/g, this.generateNotesSection(quotation));
        
        return processedTemplate;
    }

    generateAdditionalServicesSection(quotation) {
        if (!quotation.additionalServices || quotation.additionalServices.length === 0) {
            return '<w:p><w:r><w:t>추가 서비스: 없음</w:t></w:r></w:p>';
        }
        
        let servicesHTML = '<w:p><w:r><w:t>추가 서비스:</w:t></w:r></w:p>';
        
        quotation.additionalServices.forEach(service => {
            servicesHTML += `
                <w:p>
                    <w:r>
                        <w:t>${service.name}: ₩${service.amount.toLocaleString()}</w:t>
                    </w:r>
                </w:p>
            `;
        });
        
        return servicesHTML;
    }

    generateQuotationNumber() {
        const date = new Date();
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
        
        return `LRQA-${year}${month}${day}-${random}`;
    }

    getIndustryName(industryCode) {
        const industries = {
            'manufacturing': '제조업',
            'construction': '건설업',
            'service': '서비스업',
            'trade': '무역업',
            'other': '기타'
        };
        return industries[industryCode] || industryCode;
    }

    getComplexityName(complexityCode) {
        const complexities = {
            'low': '낮음',
            'medium': '보통',
            'high': '높음'
        };
        return complexities[complexityCode] || complexityCode;
    }

    getSelectedStandardsText(isoStandards) {
        if (!isoStandards || isoStandards.length === 0) {
            return '선택되지 않음';
        }
        
        const standardNames = {
            '9001': 'ISO 9001',
            '14001': 'ISO 14001',
            '45001': 'ISO 45001',
            '27001': 'ISO 27001',
            '22000': 'ISO 22000',
            '13485': 'ISO 13485'
        };
        
        return isoStandards.map(std => standardNames[std] || std).join(', ');
    }

    // 필수 XML 파일들 생성
    getContentTypesXML() {
        return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>`;
    }

    getRelsXML() {
        return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>`;
    }

    getDocumentRelsXML() {
        return `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>`;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = WordDocumentGenerator;
} else {
    window.WordDocumentGenerator = WordDocumentGenerator;
}
