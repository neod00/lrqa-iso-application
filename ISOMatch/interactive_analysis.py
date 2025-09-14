#!/usr/bin/env python3
"""
대화형 리스크 분석 인터페이스
ChatGPT API를 활용한 실시간 질의응답 시스템
"""

import json
import argparse
from pathlib import Path
from chatgpt_enhanced_analyzer import ChatGPTEnhancedAnalyzer, interactive_risk_analysis

def load_company_data(company_name: str, data_dir: Path = Path("data")):
    """기존 분석 데이터 로드"""
    try:
        # 회사명으로 JSON 파일 찾기
        json_files = list(data_dir.glob(f"*{company_name}*.json"))
        if not json_files:
            print(f"❌ {company_name}에 대한 분석 데이터를 찾을 수 없습니다.")
            print("먼저 'python report.py --name \"{company_name}\" --url \"URL\"'을 실행하여 데이터를 생성해주세요.")
            return None
        
        # 가장 최근 파일 선택
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"📁 데이터 파일 로드: {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    except Exception as e:
        print(f"❌ 데이터 로드 중 오류 발생: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="ChatGPT API를 활용한 대화형 리스크 분석")
    parser.add_argument("--company", type=str, required=True, help="분석할 회사명")
    parser.add_argument("--api-key", type=str, help="OpenAI API 키 (환경변수 OPENAI_API_KEY에서도 읽음)")
    parser.add_argument("--data-dir", type=str, default="data", help="데이터 디렉토리 경로")
    
    args = parser.parse_args()
    
    # API 키 설정
    api_key = args.api_key or "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"
    
    print(f"🤖 {args.company} 대화형 리스크 분석 시스템")
    print("=" * 60)
    
    # 기존 분석 데이터 로드
    company_data = load_company_data(args.company, Path(args.data_dir))
    
    if company_data:
        print(f"✅ {args.company} 분석 데이터 로드 완료")
        print(f"📊 뉴스 기사: {len(company_data.get('news', []))}건")
        print(f"📱 소셜미디어: {len(company_data.get('social_media', []))}건")
        print(f"📋 공시 정보: {len(company_data.get('filings', []))}건")
        print(f"🎯 리스크 점수: {company_data.get('risk', {}).get('risk_score_0to1', 'N/A')}")
        
        if 'chatgpt_enhanced_analysis' in company_data:
            print("🤖 ChatGPT AI 분석 결과가 포함되어 있습니다.")
        else:
            print("⚠️  ChatGPT AI 분석 결과가 없습니다. 기본 데이터로 분석을 진행합니다.")
        
        # 대화형 분석 시작
        interactive_risk_analysis(args.company, api_key)
    else:
        print("❌ 분석을 진행할 수 없습니다.")

if __name__ == "__main__":
    main()
