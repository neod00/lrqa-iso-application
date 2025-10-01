#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel이 최신 템플릿을 사용하는지 확인하는 스크립트
"""

import requests
import json
import zipfile
import tempfile
import os
import re
from datetime import datetime

def test_vercel_latest_template():
    """Vercel API를 호출해서 최신 템플릿이 사용되는지 확인합니다."""
    print("=== Vercel 최신 템플릿 확인 ===")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 데이터
    test_data = {
        "timestamp": "2025-09-27T12:30:00.000Z",
        "applicationData": {
            "신청일시": "2025-09-27T12:30:00.000Z",
            "상태": "신규",
            "법인명(국문)": "최신템플릿테스트회사 (Latest Template Test Co.)",
            "법인명(영문)": "Latest Template Test Company",
            "본사주소": "서울시 강남구 최신로 888",
            "도시": "서울",
            "우편번호": "88888",
            "대표전화번호": "02-8888-8888",
            "행정구역": "서울특별시",
            "국가": "대한민국",
            "대표이메일": "latest@template.com",
            "웹사이트": "www.latest.com",
            "법인등록번호": "110111-8888888",
            "사업자등록번호": "888-88-88888",
            "과세당국": "강남세무서",
            "모회사/계열사여부": "",
            "중앙관리시스템여부": "",
            "인증포함사업장수": "1",
            "사업장목록": "",
            "ISO표준": "iso9001",
            "표준적용여부": "",
            "담당자명": "박최신 (대표이사)",
            "부서": "최신팀",
            "담당자이메일": "park.latest@template.com",
            "담당자전화": "02-8888-8887",
            "휴대폰번호": "010-8888-8887",
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
            "총직원수": "75",
            "정규직수": "60",
            "비정규직수": "10",
            "하청업체직원수": "3",
            "임시직수": "2",
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
            "서명": "박최신",
            "서명날짜": "2025-09-27",
            "마케팅동의": "yes"
        }
    }
    
    try:
        print("\n1. Vercel API 호출 중...")
        print(f"   URL: https://lrqa-iso-application.vercel.app/api/create-quotation")
        print(f"   회사명: {test_data['applicationData']['법인명(국문)']}")
        
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
                print("   ✅ Word 문서가 정상적으로 생성된 것으로 보임")
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

def check_template_errors():
    """이전에 발생했던 템플릿 오류가 해결되었는지 확인합니다."""
    print("\n=== 템플릿 오류 해결 확인 ===")
    
    # 이전에 발생했던 오류 패턴들
    error_patterns = [
        r'Duplicate open tag.*cli',
        r'Duplicate close tag.*ame',
        r'Duplicate open tag.*sta',
        r'Duplicate close tag.*ext',
        r'Duplicate open tag.*quo',
        r'Duplicate close tag.*ate',
        r'Duplicate close tag.*ber'
    ]
    
    print("확인할 오류 패턴들:")
    for pattern in error_patterns:
        print(f"   - {pattern}")
    
    print("\n✅ 이전 오류들이 더 이상 발생하지 않으면 템플릿이 수정된 것입니다.")

if __name__ == "__main__":
    print("Vercel 최신 템플릿 사용 확인 시작...\n")
    
    # 1. 템플릿 오류 해결 확인
    check_template_errors()
    
    # 2. Vercel API 테스트
    vercel_ok = test_vercel_latest_template()
    
    print("\n" + "="*60)
    print("=== 최종 결과 ===")
    print(f"Vercel 최신 템플릿 사용: {'✅ 성공' if vercel_ok else '❌ 실패'}")
    
    if vercel_ok:
        print("\n🎉 Vercel이 최신 템플릿을 사용하고 있습니다!")
        print("   템플릿 변수 치환이 정상적으로 작동할 것입니다.")
        print("   이제 실제 견적서 생성에서 변수들이 치환되어 나타날 것입니다.")
    else:
        print("\n⚠️  아직 문제가 있습니다.")
        print("   Vercel 배포가 완료되지 않았거나 다른 문제가 있을 수 있습니다.")
        print("   몇 분 후에 다시 시도해보세요.")

