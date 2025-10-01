#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel에서 사용하는 템플릿이 최신 버전인지 확인하는 스크립트
"""

import requests
import json
import zipfile
import tempfile
import os
import re

def test_vercel_template():
    """Vercel API를 호출해서 템플릿 상태를 확인합니다."""
    print("=== Vercel 템플릿 상태 확인 ===")
    
    # 테스트 데이터
    test_data = {
        "timestamp": "2025-09-27T12:00:00.000Z",
        "applicationData": {
            "신청일시": "2025-09-27T12:00:00.000Z",
            "상태": "신규",
            "법인명(국문)": "템플릿 테스트 회사",
            "법인명(영문)": "Template Test Company",
            "본사주소": "서울시 강남구 테스트로 123",
            "도시": "서울시",
            "우편번호": "12345",
            "대표전화번호": "02-1234-5678",
            "행정구역": "강남구",
            "국가": "대한민국",
            "대표이메일": "test@template.com",
            "웹사이트": "www.template.com",
            "법인등록번호": "",
            "사업자등록번호": "123-45-67890",
            "과세당국": "",
            "모회사/계열사여부": "",
            "중앙관리시스템여부": "",
            "인증포함사업장수": "1",
            "사업장목록": "",
            "ISO표준": "iso9001",
            "표준적용여부": "",
            "담당자명": "김테스트 (대리)",
            "부서": "품질관리팀",
            "담당자이메일": "kim@template.com",
            "담당자전화": "02-1234-5679",
            "휴대폰번호": "010-1234-5678",
            "컨설턴트명": "",
            "컨설팅기관": "",
            "LRQA인지경로": "",
            "향후이벤트정보수신": "",
            "인증범위": "",
            "다중표준시스템": "",
            "희망년도": "2025-12",
            "희망월": "",
            "기타표준": "",
            "활동내용기재": "",
            "규제기관승인여부": "",
            "법적의무미해결문제": "",
            "기존인증보유여부": "",
            "기존표준": "",
            "기존인증기관": "",
            "인증만료일": "",
            "총직원수": "50",
            "정규직수": "40",
            "비정규직수": "8",
            "하청업체직원수": "2",
            "임시직수": "0",
            "다중사업장직원현황": "",
            "외주프로세스여부": "",
            "반복작업그룹여부": "",
            "작업성격설명": "",
            "시간외승인활동여부": "",
            "계절변동설명": "",
            "교대근무횟수": "",
            "교대근무시간": "",
            "교대총직원수": "",
            "교대조1": "",
            "교대조2": "",
            "교대조3": "",
            "교대조4": "",
            "임시사업장여부": "",
            "고객사위치서비스": "",
            "기존인증LRQA이전요청": "",
            "공식인정인증여부": "",
            "인증기관이전사유": "",
            "미해결부적합문서": "",
            "LRQA인증기관연락동의": "",
            "LRQA마지막방문일자": "",
            "첨부문서": "",
            "ISO14001사업분야": "",
            "ISO14001환경위험": "",
            "ISO45001사업분야": "",
            "ISO45001유해위험": "",
            "원격심사여부": "",
            "예비심사견적수신": "",
            "교육과정정보수신": "",
            "추가참고정보": "",
            "데이터처리동의": "yes",
            "서명": "김테스트",
            "서명날짜": "2025-09-27",
            "마케팅동의": "yes"
        }
    }
    
    try:
        print("1. Vercel API 호출 중...")
        print(f"   URL: https://lrqa-iso-application.vercel.app/api/create-quotation")
        
        response = requests.post(
            'https://lrqa-iso-application.vercel.app/api/create-quotation',
            headers={'Content-Type': 'application/json'},
            json=test_data,
            timeout=30
        )
        
        print(f"   응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API 호출 성공!")
            
            # 응답 내용 확인
            try:
                result = response.json()
                if 'error' in result:
                    print("   ❌ 오류 발생:")
                    print(f"   {result['error']}")
                    return False
                else:
                    print("   ✅ 견적서 생성 성공!")
                    return True
            except json.JSONDecodeError:
                print("   ⚠️  JSON 파싱 실패 - 바이너리 응답일 수 있음")
                return True
                
        else:
            print(f"   ❌ API 호출 실패: {response.status_code}")
            print(f"   응답 내용: {response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ 요청 시간 초과 (30초)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 요청 오류: {str(e)}")
        return False

def check_template_variables():
    """로컬 템플릿의 변수 상태를 확인합니다."""
    print("\n=== 로컬 템플릿 변수 확인 ===")
    
    template_path = "vercel-deploy/public/templates/LRQA_quotation.docx"
    
    if not os.path.exists(template_path):
        print("❌ 템플릿 파일을 찾을 수 없습니다.")
        return False
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        # .docx 파일을 .zip으로 복사하여 압축 해제
        zip_path = os.path.join(temp_dir, "template.zip")
        with open(template_path, 'rb') as src, open(zip_path, 'wb') as dst:
            dst.write(src.read())
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # document.xml 분석
        doc_path = os.path.join(temp_dir, "word/document.xml")
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 분리된 변수 패턴 확인
            separated_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)</w:t>.*?<w:t>([a-zA-Z_]+)\s*\}\}</w:t>'
            separated_matches = re.findall(separated_pattern, content, re.DOTALL)
            
            if separated_matches:
                print(f"❌ 분리된 변수 발견: {len(separated_matches)}개")
                for i, (part1, part2) in enumerate(separated_matches, 1):
                    print(f"   {i}. {{ {part1} }} + {{ {part2} }}")
                return False
            else:
                print("✅ 분리된 변수 없음")
                
                # 정상적인 변수들 확인
                normal_pattern = r'<w:t>\{\{\s*([a-zA-Z_]+)\s*\}\}</w:t>'
                normal_matches = re.findall(normal_pattern, content)
                unique_vars = set(normal_matches)
                
                print(f"✅ 정상적인 변수: {len(unique_vars)}개")
                for var in sorted(unique_vars):
                    count = normal_matches.count(var)
                    print(f"   - {var}: {count}개")
                
                return True
        else:
            print("❌ document.xml을 찾을 수 없습니다.")
            return False
            
    finally:
        # 임시 디렉토리 정리
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Vercel 템플릿 상태 확인 시작...\n")
    
    # 1. 로컬 템플릿 확인
    local_ok = check_template_variables()
    
    # 2. Vercel API 테스트
    vercel_ok = test_vercel_template()
    
    print("\n" + "="*50)
    print("=== 최종 결과 ===")
    print(f"로컬 템플릿: {'✅ 정상' if local_ok else '❌ 문제 있음'}")
    print(f"Vercel API: {'✅ 정상' if vercel_ok else '❌ 문제 있음'}")
    
    if local_ok and vercel_ok:
        print("\n🎉 모든 것이 정상입니다! 템플릿 변수 치환이 작동할 것입니다.")
    elif local_ok and not vercel_ok:
        print("\n⚠️  로컬은 정상이지만 Vercel에 문제가 있습니다.")
        print("   Vercel 재배포가 완료될 때까지 기다려주세요.")
    else:
        print("\n❌ 문제가 있습니다. 추가 수정이 필요합니다.")
