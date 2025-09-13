#!/usr/bin/env python3
"""
웹 신청서 데이터로 견적서 생성 테스트
"""

import json
import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 모듈들을 직접 import
from models import (
    Organization, Site, IntegrationInputs, Options, 
    StandardType, QuoteResult, ProgramBreakdown, ComplexityLevel,
    MandayTable
)
from quote_template import generate_lrqa_quotation_docx

def load_md_tables():
    """MD 테이블 데이터 로드"""
    md_tables = [
        # ISO 9001 테이블
        MandayTable(1, 10, ComplexityLevel.SMALL, 2.0, StandardType.ISO9001),
        MandayTable(11, 25, ComplexityLevel.SMALL, 3.0, StandardType.ISO9001),
        MandayTable(26, 45, ComplexityLevel.SMALL, 4.0, StandardType.ISO9001),
        MandayTable(46, 65, ComplexityLevel.SMALL, 5.0, StandardType.ISO9001),
        MandayTable(66, 85, ComplexityLevel.SMALL, 6.0, StandardType.ISO9001),
        MandayTable(86, 110, ComplexityLevel.MEDIUM, 7.0, StandardType.ISO9001),
        MandayTable(111, 140, ComplexityLevel.MEDIUM, 8.0, StandardType.ISO9001),
        MandayTable(141, 175, ComplexityLevel.MEDIUM, 9.0, StandardType.ISO9001),
        MandayTable(176, 215, ComplexityLevel.MEDIUM, 10.0, StandardType.ISO9001),
        MandayTable(216, 260, ComplexityLevel.MEDIUM, 11.0, StandardType.ISO9001),
        MandayTable(261, 310, ComplexityLevel.LARGE, 12.0, StandardType.ISO9001),
        MandayTable(311, 365, ComplexityLevel.LARGE, 13.0, StandardType.ISO9001),
        MandayTable(366, 425, ComplexityLevel.LARGE, 14.0, StandardType.ISO9001),
        MandayTable(426, 490, ComplexityLevel.LARGE, 15.0, StandardType.ISO9001),
        MandayTable(491, 560, ComplexityLevel.LARGE, 16.0, StandardType.ISO9001),
        MandayTable(561, 635, ComplexityLevel.LARGE, 17.0, StandardType.ISO9001),
        MandayTable(636, 715, ComplexityLevel.LARGE, 18.0, StandardType.ISO9001),
        MandayTable(716, 800, ComplexityLevel.LARGE, 19.0, StandardType.ISO9001),
        MandayTable(801, 890, ComplexityLevel.LARGE, 20.0, StandardType.ISO9001),
        MandayTable(891, 985, ComplexityLevel.LARGE, 21.0, StandardType.ISO9001),
        MandayTable(986, 1085, ComplexityLevel.LARGE, 22.0, StandardType.ISO9001),
        MandayTable(1086, 1190, ComplexityLevel.LARGE, 23.0, StandardType.ISO9001),
        MandayTable(1191, 1300, ComplexityLevel.LARGE, 24.0, StandardType.ISO9001),
        MandayTable(1301, 1415, ComplexityLevel.LARGE, 25.0, StandardType.ISO9001),
        MandayTable(1416, 1535, ComplexityLevel.LARGE, 26.0, StandardType.ISO9001),
        MandayTable(1536, 1660, ComplexityLevel.LARGE, 27.0, StandardType.ISO9001),
        MandayTable(1661, 1790, ComplexityLevel.LARGE, 28.0, StandardType.ISO9001),
        MandayTable(1791, 1925, ComplexityLevel.LARGE, 29.0, StandardType.ISO9001),
        MandayTable(1926, 2065, ComplexityLevel.LARGE, 30.0, StandardType.ISO9001),
        MandayTable(2066, 2210, ComplexityLevel.LARGE, 31.0, StandardType.ISO9001),
        MandayTable(2211, 2360, ComplexityLevel.LARGE, 32.0, StandardType.ISO9001),
        MandayTable(2361, 2515, ComplexityLevel.LARGE, 33.0, StandardType.ISO9001),
        MandayTable(2516, 2675, ComplexityLevel.LARGE, 34.0, StandardType.ISO9001),
        MandayTable(2676, 2840, ComplexityLevel.LARGE, 35.0, StandardType.ISO9001),
        MandayTable(2841, 3010, ComplexityLevel.LARGE, 36.0, StandardType.ISO9001),
        MandayTable(3011, 3185, ComplexityLevel.LARGE, 37.0, StandardType.ISO9001),
        MandayTable(3186, 3365, ComplexityLevel.LARGE, 38.0, StandardType.ISO9001),
        MandayTable(3366, 3550, ComplexityLevel.LARGE, 39.0, StandardType.ISO9001),
        MandayTable(3551, 3740, ComplexityLevel.LARGE, 40.0, StandardType.ISO9001),
        MandayTable(3741, 3935, ComplexityLevel.LARGE, 41.0, StandardType.ISO9001),
        MandayTable(3936, 4135, ComplexityLevel.LARGE, 42.0, StandardType.ISO9001),
        MandayTable(4136, 4340, ComplexityLevel.LARGE, 43.0, StandardType.ISO9001),
        MandayTable(4341, 4550, ComplexityLevel.LARGE, 44.0, StandardType.ISO9001),
        MandayTable(4551, 4765, ComplexityLevel.LARGE, 45.0, StandardType.ISO9001),
        MandayTable(4766, 4985, ComplexityLevel.LARGE, 46.0, StandardType.ISO9001),
        MandayTable(4986, 5210, ComplexityLevel.LARGE, 47.0, StandardType.ISO9001),
        MandayTable(5211, 5440, ComplexityLevel.LARGE, 48.0, StandardType.ISO9001),
        MandayTable(5441, 5675, ComplexityLevel.LARGE, 49.0, StandardType.ISO9001),
        MandayTable(5676, 5915, ComplexityLevel.LARGE, 50.0, StandardType.ISO9001),
        MandayTable(5916, 6160, ComplexityLevel.LARGE, 51.0, StandardType.ISO9001),
        MandayTable(6161, 6410, ComplexityLevel.LARGE, 52.0, StandardType.ISO9001),
        MandayTable(6411, 6665, ComplexityLevel.LARGE, 53.0, StandardType.ISO9001),
        MandayTable(6666, 6925, ComplexityLevel.LARGE, 54.0, StandardType.ISO9001),
        MandayTable(6926, 7190, ComplexityLevel.LARGE, 55.0, StandardType.ISO9001),
        MandayTable(7191, 7460, ComplexityLevel.LARGE, 56.0, StandardType.ISO9001),
        MandayTable(7461, 7735, ComplexityLevel.LARGE, 57.0, StandardType.ISO9001),
        MandayTable(7736, 8015, ComplexityLevel.LARGE, 58.0, StandardType.ISO9001),
        MandayTable(8016, 8300, ComplexityLevel.LARGE, 59.0, StandardType.ISO9001),
        MandayTable(8301, 8590, ComplexityLevel.LARGE, 60.0, StandardType.ISO9001),
        MandayTable(8591, 8885, ComplexityLevel.LARGE, 61.0, StandardType.ISO9001),
        MandayTable(8886, 9185, ComplexityLevel.LARGE, 62.0, StandardType.ISO9001),
        MandayTable(9186, 9490, ComplexityLevel.LARGE, 63.0, StandardType.ISO9001),
        MandayTable(9491, 9800, ComplexityLevel.LARGE, 64.0, StandardType.ISO9001),
        MandayTable(9801, 10115, ComplexityLevel.LARGE, 65.0, StandardType.ISO9001),
        MandayTable(10116, 10435, ComplexityLevel.LARGE, 66.0, StandardType.ISO9001),
        MandayTable(10436, 10760, ComplexityLevel.LARGE, 67.0, StandardType.ISO9001),
        MandayTable(10761, 11090, ComplexityLevel.LARGE, 68.0, StandardType.ISO9001),
        MandayTable(11091, 11425, ComplexityLevel.LARGE, 69.0, StandardType.ISO9001),
        MandayTable(11426, 11765, ComplexityLevel.LARGE, 70.0, StandardType.ISO9001),
        MandayTable(11766, 12110, ComplexityLevel.LARGE, 71.0, StandardType.ISO9001),
        MandayTable(12111, 12460, ComplexityLevel.LARGE, 72.0, StandardType.ISO9001),
        MandayTable(12461, 12815, ComplexityLevel.LARGE, 73.0, StandardType.ISO9001),
        MandayTable(12816, 13175, ComplexityLevel.LARGE, 74.0, StandardType.ISO9001),
        MandayTable(13176, 13540, ComplexityLevel.LARGE, 75.0, StandardType.ISO9001),
        MandayTable(13541, 13910, ComplexityLevel.LARGE, 76.0, StandardType.ISO9001),
        MandayTable(13911, 14285, ComplexityLevel.LARGE, 77.0, StandardType.ISO9001),
        MandayTable(14286, 14665, ComplexityLevel.LARGE, 78.0, StandardType.ISO9001),
        MandayTable(14666, 15050, ComplexityLevel.LARGE, 79.0, StandardType.ISO9001),
        MandayTable(15051, 15440, ComplexityLevel.LARGE, 80.0, StandardType.ISO9001),
        MandayTable(15441, 15835, ComplexityLevel.LARGE, 81.0, StandardType.ISO9001),
        MandayTable(15836, 16235, ComplexityLevel.LARGE, 82.0, StandardType.ISO9001),
        MandayTable(16236, 16640, ComplexityLevel.LARGE, 83.0, StandardType.ISO9001),
        MandayTable(16641, 17050, ComplexityLevel.LARGE, 84.0, StandardType.ISO9001),
        MandayTable(17051, 17465, ComplexityLevel.LARGE, 85.0, StandardType.ISO9001),
        MandayTable(17466, 17885, ComplexityLevel.LARGE, 86.0, StandardType.ISO9001),
        MandayTable(17886, 18310, ComplexityLevel.LARGE, 87.0, StandardType.ISO9001),
        MandayTable(18311, 18740, ComplexityLevel.LARGE, 88.0, StandardType.ISO9001),
        MandayTable(18741, 19175, ComplexityLevel.LARGE, 89.0, StandardType.ISO9001),
        MandayTable(19176, 19615, ComplexityLevel.LARGE, 90.0, StandardType.ISO9001),
        MandayTable(19616, 20060, ComplexityLevel.LARGE, 91.0, StandardType.ISO9001),
        MandayTable(20061, 20510, ComplexityLevel.LARGE, 92.0, StandardType.ISO9001),
        MandayTable(20511, 20965, ComplexityLevel.LARGE, 93.0, StandardType.ISO9001),
        MandayTable(20966, 21425, ComplexityLevel.LARGE, 94.0, StandardType.ISO9001),
        MandayTable(21426, 21890, ComplexityLevel.LARGE, 95.0, StandardType.ISO9001),
        MandayTable(21891, 22360, ComplexityLevel.LARGE, 96.0, StandardType.ISO9001),
        MandayTable(22361, 22835, ComplexityLevel.LARGE, 97.0, StandardType.ISO9001),
        MandayTable(22836, 23315, ComplexityLevel.LARGE, 98.0, StandardType.ISO9001),
        MandayTable(23316, 23800, ComplexityLevel.LARGE, 99.0, StandardType.ISO9001),
        MandayTable(23801, 24290, ComplexityLevel.LARGE, 100.0, StandardType.ISO9001),
        MandayTable(24291, 24785, ComplexityLevel.LARGE, 101.0, StandardType.ISO9001),
        MandayTable(24786, 25285, ComplexityLevel.LARGE, 102.0, StandardType.ISO9001),
        MandayTable(25286, 25790, ComplexityLevel.LARGE, 103.0, StandardType.ISO9001),
        MandayTable(25791, 26300, ComplexityLevel.LARGE, 104.0, StandardType.ISO9001),
        MandayTable(26301, 26815, ComplexityLevel.LARGE, 105.0, StandardType.ISO9001),
        MandayTable(26816, 27335, ComplexityLevel.LARGE, 106.0, StandardType.ISO9001),
        MandayTable(27336, 27860, ComplexityLevel.LARGE, 107.0, StandardType.ISO9001),
        MandayTable(27861, 28390, ComplexityLevel.LARGE, 108.0, StandardType.ISO9001),
        MandayTable(28391, 28925, ComplexityLevel.LARGE, 109.0, StandardType.ISO9001),
        MandayTable(28926, 29465, ComplexityLevel.LARGE, 110.0, StandardType.ISO9001),
        MandayTable(29466, 30010, ComplexityLevel.LARGE, 111.0, StandardType.ISO9001),
        MandayTable(30011, 30560, ComplexityLevel.LARGE, 112.0, StandardType.ISO9001),
        MandayTable(30561, 31115, ComplexityLevel.LARGE, 113.0, StandardType.ISO9001),
        MandayTable(31116, 31675, ComplexityLevel.LARGE, 114.0, StandardType.ISO9001),
        MandayTable(31676, 32240, ComplexityLevel.LARGE, 115.0, StandardType.ISO9001),
        MandayTable(32241, 32810, ComplexityLevel.LARGE, 116.0, StandardType.ISO9001),
        MandayTable(32811, 33385, ComplexityLevel.LARGE, 117.0, StandardType.ISO9001),
        MandayTable(33386, 33965, ComplexityLevel.LARGE, 118.0, StandardType.ISO9001),
        MandayTable(33966, 34550, ComplexityLevel.LARGE, 119.0, StandardType.ISO9001),
        MandayTable(34551, 35140, ComplexityLevel.LARGE, 120.0, StandardType.ISO9001),
        MandayTable(35141, 35735, ComplexityLevel.LARGE, 121.0, StandardType.ISO9001),
        MandayTable(35736, 36335, ComplexityLevel.LARGE, 122.0, StandardType.ISO9001),
        MandayTable(36336, 36940, ComplexityLevel.LARGE, 123.0, StandardType.ISO9001),
        MandayTable(36941, 37550, ComplexityLevel.LARGE, 124.0, StandardType.ISO9001),
        MandayTable(37551, 38165, ComplexityLevel.LARGE, 125.0, StandardType.ISO9001),
        MandayTable(38166, 38785, ComplexityLevel.LARGE, 126.0, StandardType.ISO9001),
        MandayTable(38786, 39410, ComplexityLevel.LARGE, 127.0, StandardType.ISO9001),
        MandayTable(39411, 40040, ComplexityLevel.LARGE, 128.0, StandardType.ISO9001),
        MandayTable(40041, 40675, ComplexityLevel.LARGE, 129.0, StandardType.ISO9001),
        MandayTable(40676, 41315, ComplexityLevel.LARGE, 130.0, StandardType.ISO9001),
        MandayTable(41316, 41960, ComplexityLevel.LARGE, 131.0, StandardType.ISO9001),
        MandayTable(41961, 42610, ComplexityLevel.LARGE, 132.0, StandardType.ISO9001),
        MandayTable(42611, 43265, ComplexityLevel.LARGE, 133.0, StandardType.ISO9001),
        MandayTable(43266, 43925, ComplexityLevel.LARGE, 134.0, StandardType.ISO9001),
        MandayTable(43926, 44590, ComplexityLevel.LARGE, 135.0, StandardType.ISO9001),
        MandayTable(44591, 45260, ComplexityLevel.LARGE, 136.0, StandardType.ISO9001),
        MandayTable(45261, 45935, ComplexityLevel.LARGE, 137.0, StandardType.ISO9001),
        MandayTable(45936, 46615, ComplexityLevel.LARGE, 138.0, StandardType.ISO9001),
        MandayTable(46616, 47300, ComplexityLevel.LARGE, 139.0, StandardType.ISO9001),
        MandayTable(47301, 47990, ComplexityLevel.LARGE, 140.0, StandardType.ISO9001),
        MandayTable(47991, 48685, ComplexityLevel.LARGE, 141.0, StandardType.ISO9001),
        MandayTable(48686, 49385, ComplexityLevel.LARGE, 142.0, StandardType.ISO9001),
        MandayTable(49386, 50090, ComplexityLevel.LARGE, 143.0, StandardType.ISO9001),
        MandayTable(50091, 50800, ComplexityLevel.LARGE, 144.0, StandardType.ISO9001),
        MandayTable(50801, 51515, ComplexityLevel.LARGE, 145.0, StandardType.ISO9001),
        MandayTable(51516, 52235, ComplexityLevel.LARGE, 146.0, StandardType.ISO9001),
        MandayTable(52236, 52960, ComplexityLevel.LARGE, 147.0, StandardType.ISO9001),
        MandayTable(52961, 53690, ComplexityLevel.LARGE, 148.0, StandardType.ISO9001),
        MandayTable(53691, 54425, ComplexityLevel.LARGE, 149.0, StandardType.ISO9001),
        MandayTable(54426, 55165, ComplexityLevel.LARGE, 150.0, StandardType.ISO9001),
        MandayTable(55166, 55910, ComplexityLevel.LARGE, 151.0, StandardType.ISO9001),
        MandayTable(55911, 56660, ComplexityLevel.LARGE, 152.0, StandardType.ISO9001),
        MandayTable(56661, 57415, ComplexityLevel.LARGE, 153.0, StandardType.ISO9001),
        MandayTable(57416, 58175, ComplexityLevel.LARGE, 154.0, StandardType.ISO9001),
        MandayTable(58176, 58940, ComplexityLevel.LARGE, 155.0, StandardType.ISO9001),
        MandayTable(58941, 59710, ComplexityLevel.LARGE, 156.0, StandardType.ISO9001),
        MandayTable(59711, 60485, ComplexityLevel.LARGE, 157.0, StandardType.ISO9001),
        MandayTable(60486, 61265, ComplexityLevel.LARGE, 158.0, StandardType.ISO9001),
        MandayTable(61266, 62050, ComplexityLevel.LARGE, 159.0, StandardType.ISO9001),
        MandayTable(62051, 62840, ComplexityLevel.LARGE, 160.0, StandardType.ISO9001),
        MandayTable(62841, 63635, ComplexityLevel.LARGE, 161.0, StandardType.ISO9001),
        MandayTable(63636, 64435, ComplexityLevel.LARGE, 162.0, StandardType.ISO9001),
        MandayTable(64436, 65240, ComplexityLevel.LARGE, 163.0, StandardType.ISO9001),
        MandayTable(65241, 66050, ComplexityLevel.LARGE, 164.0, StandardType.ISO9001),
        MandayTable(66051, 66865, ComplexityLevel.LARGE, 165.0, StandardType.ISO9001),
        MandayTable(66866, 67685, ComplexityLevel.LARGE, 166.0, StandardType.ISO9001),
        MandayTable(67686, 68510, ComplexityLevel.LARGE, 167.0, StandardType.ISO9001),
        MandayTable(68511, 69340, ComplexityLevel.LARGE, 168.0, StandardType.ISO9001),
        MandayTable(69341, 70175, ComplexityLevel.LARGE, 169.0, StandardType.ISO9001),
        MandayTable(70176, 71015, ComplexityLevel.LARGE, 170.0, StandardType.ISO9001),
        MandayTable(71016, 71860, ComplexityLevel.LARGE, 171.0, StandardType.ISO9001),
        MandayTable(71861, 72710, ComplexityLevel.LARGE, 172.0, StandardType.ISO9001),
        MandayTable(72711, 73565, ComplexityLevel.LARGE, 173.0, StandardType.ISO9001),
        MandayTable(73566, 74425, ComplexityLevel.LARGE, 174.0, StandardType.ISO9001),
        MandayTable(74426, 75290, ComplexityLevel.LARGE, 175.0, StandardType.ISO9001),
        MandayTable(75291, 76160, ComplexityLevel.LARGE, 176.0, StandardType.ISO9001),
        MandayTable(76161, 77035, ComplexityLevel.LARGE, 177.0, StandardType.ISO9001),
        MandayTable(77036, 77915, ComplexityLevel.LARGE, 178.0, StandardType.ISO9001),
        MandayTable(77916, 78800, ComplexityLevel.LARGE, 179.0, StandardType.ISO9001),
        MandayTable(78801, 79690, ComplexityLevel.LARGE, 180.0, StandardType.ISO9001),
        MandayTable(79691, 80585, ComplexityLevel.LARGE, 181.0, StandardType.ISO9001),
        MandayTable(80586, 81485, ComplexityLevel.LARGE, 182.0, StandardType.ISO9001),
        MandayTable(81486, 82390, ComplexityLevel.LARGE, 183.0, StandardType.ISO9001),
        MandayTable(82391, 83300, ComplexityLevel.LARGE, 184.0, StandardType.ISO9001),
        MandayTable(83301, 84215, ComplexityLevel.LARGE, 185.0, StandardType.ISO9001),
        MandayTable(84216, 85135, ComplexityLevel.LARGE, 186.0, StandardType.ISO9001),
        MandayTable(85136, 86060, ComplexityLevel.LARGE, 187.0, StandardType.ISO9001),
        MandayTable(86061, 86990, ComplexityLevel.LARGE, 188.0, StandardType.ISO9001),
        MandayTable(86991, 87925, ComplexityLevel.LARGE, 189.0, StandardType.ISO9001),
        MandayTable(87926, 88865, ComplexityLevel.LARGE, 190.0, StandardType.ISO9001),
        MandayTable(88866, 89810, ComplexityLevel.LARGE, 191.0, StandardType.ISO9001),
        MandayTable(89811, 90760, ComplexityLevel.LARGE, 192.0, StandardType.ISO9001),
        MandayTable(90761, 91715, ComplexityLevel.LARGE, 193.0, StandardType.ISO9001),
        MandayTable(91716, 92675, ComplexityLevel.LARGE, 194.0, StandardType.ISO9001),
        MandayTable(92676, 93640, ComplexityLevel.LARGE, 195.0, StandardType.ISO9001),
        MandayTable(93641, 94610, ComplexityLevel.LARGE, 196.0, StandardType.ISO9001),
        MandayTable(94611, 95585, ComplexityLevel.LARGE, 197.0, StandardType.ISO9001),
        MandayTable(95586, 96565, ComplexityLevel.LARGE, 198.0, StandardType.ISO9001),
        MandayTable(96566, 97550, ComplexityLevel.LARGE, 199.0, StandardType.ISO9001),
        MandayTable(97551, 98540, ComplexityLevel.LARGE, 200.0, StandardType.ISO9001),
    ]
    
    # ISO 14001과 ISO 45001 테이블 추가 (ISO 9001과 동일한 구조)
    for table in md_tables[:]:
        if table.standard_type == StandardType.ISO9001:
            # ISO 14001 테이블 추가
            md_tables.append(MandayTable(
                table.enp_min, table.enp_max, table.complexity, 
                table.stage2_days, StandardType.ISO14001
            ))
            # ISO 45001 테이블 추가
            md_tables.append(MandayTable(
                table.enp_min, table.enp_max, table.complexity, 
                table.stage2_days, StandardType.ISO45001
            ))
    
    return md_tables

def calculate_enp(site):
    """ENP 계산"""
    total_headcount = site.total_headcount
    regular_employees = int(total_headcount * 0.85)  # 85% 정규직
    non_regular_employees = int(total_headcount * 0.10)  # 10% 비정규직
    contractors = int(total_headcount * 0.05)  # 5% 협력업체
    
    # ENP 계산: 정규직 + 외주 - 파트타임(50%) + 교대근무(50%) + 계절성/반복공정 조정
    enp = regular_employees + contractors - (non_regular_employees * 0.5) + (total_headcount * 0.1)
    
    return max(1, int(enp))

def main():
    """메인 함수"""
    print("=== 웹 신청서 데이터로 견적서 생성 테스트 ===")
    
    # 웹 신청서 데이터 (실제 수집된 데이터)
    web_form_data = {
        "company": {
            "name": "아이폰 주식회사",
            "nameEn": "iPhone Corporation Ltd.",
            "address": "서울시 광진구 중곡동 45",
            "phone": "02-1234-5678",
            "email": "contact@iphone-corp.com",
            "website": "https://www.iphone-corp.com"
        },
        "contact": {
            "name": "김아이폰",
            "department": "품질경영팀",
            "email": "kim.iphone@iphone-corp.com",
            "phone": "02-1234-5679",
            "mobile": "010-1234-5678"
        },
        "standards": ["ISO 9001", "ISO 14001", "ISO 45001"],
        "sites": [
            {
                "name": "사업장 1",
                "address": "서울시 강남구 테헤란로 123",
                "activity": "스마트폰 제조 및 개발",
                "employees": 150
            },
            {
                "name": "사업장 2", 
                "address": "부산시 해운대구 센텀중앙로 456",
                "activity": "스마트폰 부품 제조",
                "employees": 80
            },
            {
                "name": "사업장 3",
                "address": "대구시 수성구 동대구로 789", 
                "activity": "고객 서비스 및 영업",
                "employees": 30
            }
        ],
        "employees": {
            "total": 590,
            "regular": 500,
            "nonRegular": 90,
            "contractors": 20
        }
    }
    
    # MD 테이블 로드
    md_tables = load_md_tables()
    
    # 사업장 생성
    sites = []
    for site_data in web_form_data["sites"]:
        site = Site(
            name=site_data["name"],
            address=site_data["address"],
            standards=[StandardType.ISO9001, StandardType.ISO14001, StandardType.ISO45001],
            total_headcount=site_data["employees"]
        )
        sites.append(site)
    
    # 조직 생성
    organization = Organization(
        client_name=web_form_data["company"]["name"],
        client_name_en=web_form_data["company"]["nameEn"],
        standards=[StandardType.ISO9001, StandardType.ISO14001, StandardType.ISO45001],
        sites=sites
    )
    
    # 통합 입력 생성
    integration_inputs = IntegrationInputs(
        is_integrated=True,
        integration_level=0.8,
        shared_management_system=True,
        common_processes=True,
        same_audit_team=True
    )
    
    # 옵션 생성
    options = Options(
        stage1=True,
        stage2=True,
        surveillance=True,
        recert=True,
        day_rate=1300000.0
    )
    
    # 견적 계산 (advanced_test.py의 로직 사용)
    def calculate_enp(site: Site) -> float:
        """ENP 계산"""
        base_enp = site.total_headcount + site.contractor_count
        part_time_adjustment = site.part_time_count * 0.5  # 50% 감축
        shift_adjustment = site.shift_workers * 0.5  # 50% 추가
        seasonal_adjustment = site.seasonal_factor - 1.0  # 계절성 조정
        
        enp = base_enp - part_time_adjustment + shift_adjustment + seasonal_adjustment
        return max(1.0, enp)
    
    def find_manday_table(enp: float, standard: StandardType, md_tables: list):
        """ENP에 해당하는 MD 테이블 찾기"""
        max_table = None
        for table in md_tables:
            if table.standard_type == standard and table.enp_min <= enp <= table.enp_max:
                max_table = table
        return max_table
    
    def calculate_audit_days(enp: float, standard: StandardType, md_tables: list, options: Options) -> ProgramBreakdown:
        """심사일수 계산"""
        table = find_manday_table(enp, standard, md_tables)
        
        if not table:
            print(f"⚠️  {standard.value}에 대한 MD 테이블을 찾을 수 없습니다 (ENP: {enp})")
            return ProgramBreakdown(
                standard=standard,
                stage1_days=0.0,
                stage2_days=0.0,
                surveillance_days=0.0,
                recert_days=0.0,
                total_days=0.0
            )
        
        # Stage별 일수 계산
        stage1_days = table.stage2_days * 0.3 if options.stage1 else 0.0
        stage2_days = table.stage2_days if options.stage2 else 0.0
        surveillance_days = table.stage2_days * 0.6 if options.surveillance else 0.0
        recert_days = table.stage2_days if options.recert else 0.0
        
        total_days = stage1_days + stage2_days + surveillance_days + recert_days
        total_cost = total_days * options.day_rate
        
        return ProgramBreakdown(
            standard=standard,
            stage1_days=stage1_days,
            stage2_days=stage2_days,
            surveillance_days=surveillance_days,
            recert_days=recert_days,
            total_days=total_days
        )
    
    # 견적 계산
    breakdowns = []
    total_days = 0.0
    
    for site in organization.sites:
        enp = calculate_enp(site)
        print(f"🏭 {site.name}: ENP {enp:.1f}명")
        
        for standard in site.standards:
            breakdown = calculate_audit_days(enp, standard, md_tables, options)
            breakdowns.append(breakdown)
            total_days += breakdown.total_days
    
    # 비용 계산
    subtotal_cost = total_days * options.day_rate
    vat_amount = subtotal_cost * options.vat_rate
    total_cost = subtotal_cost + vat_amount
    
    # 견적 결과 생성
    result = QuoteResult(
        organization=organization,
        breakdowns=breakdowns,
        total_audit_days=total_days,
        subtotal_cost=subtotal_cost,
        vat_amount=vat_amount,
        total_cost=total_cost,
        created_at=datetime.now().isoformat()
    )
    
    print(f"견적 계산 완료!")
    print(f"총 심사일수: {result.total_audit_days}")
    print(f"총 견적 금액: ₩{result.total_cost:,.0f}")
    
    # 견적서를 JSON으로 저장
    output_file = "test_web_form_quotation.json"
    quotation_data = {
        "client_name": result.organization.client_name,
        "client_name_en": result.organization.client_name_en,
        "standards": [std.value for std in result.organization.standards],
        "sites": [
            {
                "name": site.name,
                "address": site.address,
                "standards": [std.value for std in site.standards],
                "total_headcount": site.total_headcount,
                "enp": calculate_enp(site)
            }
            for site in result.organization.sites
        ],
        "total_audit_days": result.total_audit_days,
        "manday_rate": options.day_rate,
        "subtotal": result.subtotal_cost,
        "vat": result.vat_amount,
        "total_cost": result.total_cost,
        "program_breakdown": [
            {
                "standard": breakdown.standard.value,
                "stage1_days": breakdown.stage1_days,
                "stage2_days": breakdown.stage2_days,
                "surveillance_days": breakdown.surveillance_days,
                "recert_days": breakdown.recert_days,
                "total_days": breakdown.total_days
            }
            for breakdown in result.breakdowns
        ],
        "generated_at": datetime.now().isoformat()
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(quotation_data, f, ensure_ascii=False, indent=2)
    
    print(f"견적서 JSON 저장 완료: {output_file}")
    
    # Word 견적서 생성
    try:
        word_output = f"../test_results/{web_form_data['company']['name']}_웹신청서_견적서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        generate_lrqa_quotation_docx(result, word_output)
        print(f"Word 견적서 생성 완료: {word_output}")
    except Exception as e:
        print(f"Word 견적서 생성 실패: {e}")

if __name__ == "__main__":
    main()
