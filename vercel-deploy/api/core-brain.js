/**
 * 핵심두뇌 API - ADJ v2.2 기반 정확한 견적 계산
 * Vercel Functions로 배포되는 핵심두뇌 엔진
 */

// 핵심두뇌 엔진 import (Python 코드를 JavaScript로 변환)
import { QuoteEngine } from '../adj_quote_engine/adj_rules_v22.js';

export default async function handler(req, res) {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Content-Type', 'application/json');

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // POST 요청만 허용
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    console.log('=== 핵심두뇌 API 호출 시작 ===');
    console.log('요청 데이터:', JSON.stringify(req.body, null, 2));

    // 요청 데이터 파싱
    const data = req.body;
    const client_name = data.client_name || 'Unknown';
    const sites_data = data.sites || [];
    const standards = data.standards || ['ISO9001'];
    const options = data.options || {};

    console.log(`핵심두뇌 계산 대상: ${client_name}`);
    console.log(`사이트 수: ${sites_data.length}`);
    console.log(`표준: ${standards.join(', ')}`);

    // 핵심두뇌 엔진 초기화
    const quoteEngine = new QuoteEngine();

    // Site 객체 생성
    const sites = sites_data.map(site_data => ({
      name: site_data.name || 'Unknown',
      address: site_data.address || '',
      standards: site_data.standards || ['ISO9001'],
      total_headcount: parseInt(site_data.total_headcount) || 0,
      business_sector: site_data.business_sector || 'MANUFACTURING',
      management_system_maturity: site_data.management_system_maturity || 'MEDIUM'
    }));

    // Organization 객체 생성
    const organization = {
      client_name: client_name,
      sites: sites,
      standards: standards,
      options: {
        stage1: options.stage1 !== false,
        stage2: options.stage2 !== false,
        surveillance: options.surveillance !== false,
        recert: options.recert !== false,
        integrated_audit: options.integrated_audit || false,
        remote_audit: options.remote_audit || false
      }
    };

    console.log('조직 정보:', JSON.stringify(organization, null, 2));

    // 핵심두뇌 계산 실행
    const result = await quoteEngine.calculate_quote(organization);

    console.log('핵심두뇌 계산 완료:', result);

    // 응답 데이터 구성
    const response = {
      success: true,
      message: '핵심두뇌 계산이 성공적으로 완료되었습니다.',
      data: {
        client_name: client_name,
        total_audit_days: result.total_audit_days,
        total_cost: result.total_cost,
        breakdowns: result.breakdowns || [],
        assumptions: result.assumptions || [],
        calculation_method: 'core_brain',
        calculation_details: {
          enp_calculation: result.enp_calculation || {},
          complexity_assessment: result.complexity_assessment || {},
          stage_calculation: result.stage_calculation || {}
        }
      }
    };

    console.log('핵심두뇌 응답:', JSON.stringify(response, null, 2));

    res.status(200).json(response);

  } catch (error) {
    console.error('핵심두뇌 계산 오류:', error);
    
    // 오류 응답
    res.status(500).json({
      success: false,
      error: '핵심두뇌 계산 중 오류가 발생했습니다.',
      message: error.message,
      details: error.stack
    });
  }
}
