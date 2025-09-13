"""
MD5/MD1/MD11 기준 심사일수 테이블

이 모듈은 IAF MD 표준에 따른 최소 심사일수 테이블을 제공합니다.
ENP(유효인원수)를 기준으로 S/M/L 복잡도 버킷으로 분류하고,
Stage2 기준일수에서 Stage1(30%), SV1(60%), Recert(100%)로 환산합니다.
"""

from typing import List, Dict, Optional
from .models import MandayTable, ComplexityLevel, StandardType


class MandayTableManager:
    """MD 테이블 관리자"""
    
    def __init__(self):
        self.tables = self._initialize_tables()
    
    def _initialize_tables(self) -> List[MandayTable]:
        """MD 테이블 초기화 - IAF MD5 표준에 따른 표준별 전용 테이블"""
        tables = []
        
        # IAF MD5 Table QMS 1 (ISO 9001) - Stage1+Stage2 총합 기준
        qms_data = [
            # Small complexity (QMS)
            (1, 10, ComplexityLevel.SMALL, 2.0),      # Stage1+Stage2 = 2일
            (11, 25, ComplexityLevel.SMALL, 3.0),     # Stage1+Stage2 = 3일
            (26, 45, ComplexityLevel.SMALL, 4.0),     # Stage1+Stage2 = 4일
            (46, 65, ComplexityLevel.SMALL, 5.0),     # Stage1+Stage2 = 5일
            (66, 85, ComplexityLevel.SMALL, 6.0),     # Stage1+Stage2 = 6일
            (86, 125, ComplexityLevel.SMALL, 7.0),    # Stage1+Stage2 = 7일
            (126, 175, ComplexityLevel.SMALL, 8.0),   # Stage1+Stage2 = 8일
            (176, 275, ComplexityLevel.SMALL, 9.0),   # Stage1+Stage2 = 9일
            (276, 425, ComplexityLevel.SMALL, 10.0),  # Stage1+Stage2 = 10일
            (426, 625, ComplexityLevel.SMALL, 11.0),  # Stage1+Stage2 = 11일 (IAF MD5 기준)
            (626, 875, ComplexityLevel.SMALL, 12.0),  # Stage1+Stage2 = 12일 (IAF MD5 기준)
            (876, 1175, ComplexityLevel.SMALL, 13.0), # Stage1+Stage2 = 13일 (IAF MD5 기준)
            (1176, 1550, ComplexityLevel.SMALL, 14.0),# Stage1+Stage2 = 14일 (IAF MD5 기준)
            (1551, 2025, ComplexityLevel.SMALL, 15.0),# Stage1+Stage2 = 15일 (IAF MD5 기준)
            (2026, 2675, ComplexityLevel.SMALL, 16.0),# Stage1+Stage2 = 16일 (IAF MD5 기준)
            (2676, 3500, ComplexityLevel.SMALL, 17.0),# Stage1+Stage2 = 17일 (IAF MD5 기준)
            (3501, 4625, ComplexityLevel.SMALL, 18.0),# Stage1+Stage2 = 18일 (IAF MD5 기준)
            (4626, 6100, ComplexityLevel.SMALL, 19.0),# Stage1+Stage2 = 19일 (IAF MD5 기준)
            (6101, 8075, ComplexityLevel.SMALL, 20.0),# Stage1+Stage2 = 20일 (IAF MD5 기준)
            (8076, 10700, ComplexityLevel.SMALL, 21.0),# Stage1+Stage2 = 21일 (IAF MD5 기준)
            (10701, 14200, ComplexityLevel.SMALL, 22.0),# Stage1+Stage2 = 22일 (IAF MD5 기준)
            (14201, 18800, ComplexityLevel.SMALL, 23.0),# Stage1+Stage2 = 23일 (IAF MD5 기준)
            (18801, 25000, ComplexityLevel.SMALL, 24.0),# Stage1+Stage2 = 24일 (IAF MD5 기준)
            
            # Medium complexity (QMS)
            (1, 10, ComplexityLevel.MEDIUM, 3.0),     # Stage1+Stage2 = 3일
            (11, 25, ComplexityLevel.MEDIUM, 4.0),    # Stage1+Stage2 = 4일
            (26, 45, ComplexityLevel.MEDIUM, 5.0),    # Stage1+Stage2 = 5일
            (46, 65, ComplexityLevel.MEDIUM, 6.0),    # Stage1+Stage2 = 6일
            (66, 85, ComplexityLevel.MEDIUM, 7.0),    # Stage1+Stage2 = 7일
            (86, 125, ComplexityLevel.MEDIUM, 8.0),   # Stage1+Stage2 = 8일
            (126, 175, ComplexityLevel.MEDIUM, 9.0),  # Stage1+Stage2 = 9일
            (176, 275, ComplexityLevel.MEDIUM, 10.0), # Stage1+Stage2 = 10일
            (276, 425, ComplexityLevel.MEDIUM, 11.0), # Stage1+Stage2 = 11일
            (426, 625, ComplexityLevel.MEDIUM, 12.0), # Stage1+Stage2 = 12일
            (626, 875, ComplexityLevel.MEDIUM, 13.0), # Stage1+Stage2 = 13일
            (876, 1175, ComplexityLevel.MEDIUM, 14.0),# Stage1+Stage2 = 14일
            (1176, 1550, ComplexityLevel.MEDIUM, 15.0),# Stage1+Stage2 = 15일
            (1551, 2025, ComplexityLevel.MEDIUM, 16.0),# Stage1+Stage2 = 16일
            (2026, 2675, ComplexityLevel.MEDIUM, 17.0),# Stage1+Stage2 = 17일
            (2676, 3500, ComplexityLevel.MEDIUM, 18.0),# Stage1+Stage2 = 18일
            (3501, 4625, ComplexityLevel.MEDIUM, 19.0),# Stage1+Stage2 = 19일
            (4626, 6100, ComplexityLevel.MEDIUM, 20.0),# Stage1+Stage2 = 20일
            (6101, 8075, ComplexityLevel.MEDIUM, 21.0),# Stage1+Stage2 = 21일
            (8076, 10700, ComplexityLevel.MEDIUM, 22.0),# Stage1+Stage2 = 22일
            (10701, 14200, ComplexityLevel.MEDIUM, 23.0),# Stage1+Stage2 = 23일
            (14201, 18800, ComplexityLevel.MEDIUM, 24.0),# Stage1+Stage2 = 24일
            (18801, 25000, ComplexityLevel.MEDIUM, 25.0),# Stage1+Stage2 = 25일
            
            # Large complexity (QMS)
            (1, 10, ComplexityLevel.LARGE, 4.0),      # Stage1+Stage2 = 4일
            (11, 25, ComplexityLevel.LARGE, 5.0),     # Stage1+Stage2 = 5일
            (26, 45, ComplexityLevel.LARGE, 6.0),     # Stage1+Stage2 = 6일
            (46, 65, ComplexityLevel.LARGE, 7.0),     # Stage1+Stage2 = 7일
            (66, 85, ComplexityLevel.LARGE, 8.0),     # Stage1+Stage2 = 8일
            (86, 125, ComplexityLevel.LARGE, 9.0),    # Stage1+Stage2 = 9일
            (126, 175, ComplexityLevel.LARGE, 10.0),  # Stage1+Stage2 = 10일
            (176, 275, ComplexityLevel.LARGE, 11.0),  # Stage1+Stage2 = 11일
            (276, 425, ComplexityLevel.LARGE, 12.0),  # Stage1+Stage2 = 12일
            (426, 625, ComplexityLevel.LARGE, 11.0),  # Stage1+Stage2 = 11일 (IAF MD5 기준)
            (626, 875, ComplexityLevel.LARGE, 14.0),  # Stage1+Stage2 = 14일
            (876, 1175, ComplexityLevel.LARGE, 15.0), # Stage1+Stage2 = 15일
            (1176, 1550, ComplexityLevel.LARGE, 16.0),# Stage1+Stage2 = 16일
            (1551, 2025, ComplexityLevel.LARGE, 17.0),# Stage1+Stage2 = 17일
            (2026, 2675, ComplexityLevel.LARGE, 18.0),# Stage1+Stage2 = 18일
            (2676, 3500, ComplexityLevel.LARGE, 19.0),# Stage1+Stage2 = 19일
            (3501, 4625, ComplexityLevel.LARGE, 20.0),# Stage1+Stage2 = 20일
            (4626, 6100, ComplexityLevel.LARGE, 21.0),# Stage1+Stage2 = 21일
            (6101, 8075, ComplexityLevel.LARGE, 22.0),# Stage1+Stage2 = 22일
            (8076, 10700, ComplexityLevel.LARGE, 23.0),# Stage1+Stage2 = 23일
            (10701, 14200, ComplexityLevel.LARGE, 24.0),# Stage1+Stage2 = 24일
            (14201, 18800, ComplexityLevel.LARGE, 25.0),# Stage1+Stage2 = 25일
            (18801, 25000, ComplexityLevel.LARGE, 26.0),# Stage1+Stage2 = 26일
        ]
        
        # IAF MD5 Table EMS 1 (ISO 14001) - 복잡도 요인별 Stage1+Stage2 총합
        ems_data = [
            # High complexity (EMS) - ENP 426-625: 16일
            (426, 625, ComplexityLevel.HIGH, 16.0),   # Stage1+Stage2 = 16일
            (626, 875, ComplexityLevel.HIGH, 17.0),   # Stage1+Stage2 = 17일
            (876, 1175, ComplexityLevel.HIGH, 18.0),  # Stage1+Stage2 = 18일
            (1176, 1550, ComplexityLevel.HIGH, 19.0), # Stage1+Stage2 = 19일
            (1551, 2025, ComplexityLevel.HIGH, 20.0), # Stage1+Stage2 = 20일
            (2026, 2675, ComplexityLevel.HIGH, 21.0), # Stage1+Stage2 = 21일
            (2676, 3500, ComplexityLevel.HIGH, 22.0), # Stage1+Stage2 = 22일
            (3501, 4625, ComplexityLevel.HIGH, 23.0), # Stage1+Stage2 = 23일
            (4626, 6100, ComplexityLevel.HIGH, 24.0), # Stage1+Stage2 = 24일
            (6101, 8075, ComplexityLevel.HIGH, 25.0), # Stage1+Stage2 = 25일
            (8076, 10700, ComplexityLevel.HIGH, 26.0),# Stage1+Stage2 = 26일
            (10701, 14200, ComplexityLevel.HIGH, 27.0),# Stage1+Stage2 = 27일
            (14201, 18800, ComplexityLevel.HIGH, 28.0),# Stage1+Stage2 = 28일
            (18801, 25000, ComplexityLevel.HIGH, 29.0),# Stage1+Stage2 = 29일
            
            # Medium complexity (EMS) - ENP 426-625: 12일
            (426, 625, ComplexityLevel.MEDIUM, 12.0), # Stage1+Stage2 = 12일
            (626, 875, ComplexityLevel.MEDIUM, 13.0), # Stage1+Stage2 = 13일
            (876, 1175, ComplexityLevel.MEDIUM, 14.0),# Stage1+Stage2 = 14일
            (1176, 1550, ComplexityLevel.MEDIUM, 15.0),# Stage1+Stage2 = 15일
            (1551, 2025, ComplexityLevel.MEDIUM, 16.0),# Stage1+Stage2 = 16일
            (2026, 2675, ComplexityLevel.MEDIUM, 17.0),# Stage1+Stage2 = 17일
            (2676, 3500, ComplexityLevel.MEDIUM, 18.0),# Stage1+Stage2 = 18일
            (3501, 4625, ComplexityLevel.MEDIUM, 19.0),# Stage1+Stage2 = 19일
            (4626, 6100, ComplexityLevel.MEDIUM, 20.0),# Stage1+Stage2 = 20일
            (6101, 8075, ComplexityLevel.MEDIUM, 21.0),# Stage1+Stage2 = 21일
            (8076, 10700, ComplexityLevel.MEDIUM, 22.0),# Stage1+Stage2 = 22일
            (10701, 14200, ComplexityLevel.MEDIUM, 23.0),# Stage1+Stage2 = 23일
            (14201, 18800, ComplexityLevel.MEDIUM, 24.0),# Stage1+Stage2 = 24일
            (18801, 25000, ComplexityLevel.MEDIUM, 25.0),# Stage1+Stage2 = 25일
            
            # Low complexity (EMS) - ENP 426-625: 9일
            (426, 625, ComplexityLevel.LOW, 9.0),     # Stage1+Stage2 = 9일
            (626, 875, ComplexityLevel.LOW, 10.0),    # Stage1+Stage2 = 10일
            (876, 1175, ComplexityLevel.LOW, 11.0),   # Stage1+Stage2 = 11일
            (1176, 1550, ComplexityLevel.LOW, 12.0),  # Stage1+Stage2 = 12일
            (1551, 2025, ComplexityLevel.LOW, 13.0),  # Stage1+Stage2 = 13일
            (2026, 2675, ComplexityLevel.LOW, 14.0),  # Stage1+Stage2 = 14일
            (2676, 3500, ComplexityLevel.LOW, 15.0),  # Stage1+Stage2 = 15일
            (3501, 4625, ComplexityLevel.LOW, 16.0),  # Stage1+Stage2 = 16일
            (4626, 6100, ComplexityLevel.LOW, 17.0),  # Stage1+Stage2 = 17일
            (6101, 8075, ComplexityLevel.LOW, 18.0),  # Stage1+Stage2 = 18일
            (8076, 10700, ComplexityLevel.LOW, 19.0), # Stage1+Stage2 = 19일
            (10701, 14200, ComplexityLevel.LOW, 20.0),# Stage1+Stage2 = 20일
            (14201, 18800, ComplexityLevel.LOW, 21.0),# Stage1+Stage2 = 21일
            (18801, 25000, ComplexityLevel.LOW, 22.0),# Stage1+Stage2 = 22일
            
            # Limited complexity (EMS) - ENP 426-625: 6일
            (426, 625, ComplexityLevel.LIMITED, 6.0), # Stage1+Stage2 = 6일
            (626, 875, ComplexityLevel.LIMITED, 7.0), # Stage1+Stage2 = 7일
            (876, 1175, ComplexityLevel.LIMITED, 8.0),# Stage1+Stage2 = 8일
            (1176, 1550, ComplexityLevel.LIMITED, 9.0),# Stage1+Stage2 = 9일
            (1551, 2025, ComplexityLevel.LIMITED, 10.0),# Stage1+Stage2 = 10일
            (2026, 2675, ComplexityLevel.LIMITED, 11.0),# Stage1+Stage2 = 11일
            (2676, 3500, ComplexityLevel.LIMITED, 12.0),# Stage1+Stage2 = 12일
            (3501, 4625, ComplexityLevel.LIMITED, 13.0),# Stage1+Stage2 = 13일
            (4626, 6100, ComplexityLevel.LIMITED, 14.0),# Stage1+Stage2 = 14일
            (6101, 8075, ComplexityLevel.LIMITED, 15.0),# Stage1+Stage2 = 15일
            (8076, 10700, ComplexityLevel.LIMITED, 16.0),# Stage1+Stage2 = 16일
            (10701, 14200, ComplexityLevel.LIMITED, 17.0),# Stage1+Stage2 = 17일
            (14201, 18800, ComplexityLevel.LIMITED, 18.0),# Stage1+Stage2 = 18일
            (18801, 25000, ComplexityLevel.LIMITED, 19.0),# Stage1+Stage2 = 19일
        ]
        
        # IAF MD5 Table OH&SMS 1 (ISO 45001) - 복잡도 요인별 Stage1+Stage2 총합
        ohsms_data = [
            # High complexity (OH&SMS) - ENP 426-625: 16일
            (426, 625, ComplexityLevel.HIGH, 16.0),   # Stage1+Stage2 = 16일
            (626, 875, ComplexityLevel.HIGH, 17.0),   # Stage1+Stage2 = 17일
            (876, 1175, ComplexityLevel.HIGH, 18.0),  # Stage1+Stage2 = 18일
            (1176, 1550, ComplexityLevel.HIGH, 19.0), # Stage1+Stage2 = 19일
            (1551, 2025, ComplexityLevel.HIGH, 20.0), # Stage1+Stage2 = 20일
            (2026, 2675, ComplexityLevel.HIGH, 21.0), # Stage1+Stage2 = 21일
            (2676, 3500, ComplexityLevel.HIGH, 22.0), # Stage1+Stage2 = 22일
            (3501, 4625, ComplexityLevel.HIGH, 23.0), # Stage1+Stage2 = 23일
            (4626, 6100, ComplexityLevel.HIGH, 24.0), # Stage1+Stage2 = 24일
            (6101, 8075, ComplexityLevel.HIGH, 25.0), # Stage1+Stage2 = 25일
            (8076, 10700, ComplexityLevel.HIGH, 26.0),# Stage1+Stage2 = 26일
            (10701, 14200, ComplexityLevel.HIGH, 27.0),# Stage1+Stage2 = 27일
            (14201, 18800, ComplexityLevel.HIGH, 28.0),# Stage1+Stage2 = 28일
            (18801, 25000, ComplexityLevel.HIGH, 29.0),# Stage1+Stage2 = 29일
            
            # Medium complexity (OH&SMS) - ENP 426-625: 12일
            (426, 625, ComplexityLevel.MEDIUM, 12.0), # Stage1+Stage2 = 12일
            (626, 875, ComplexityLevel.MEDIUM, 13.0), # Stage1+Stage2 = 13일
            (876, 1175, ComplexityLevel.MEDIUM, 14.0),# Stage1+Stage2 = 14일
            (1176, 1550, ComplexityLevel.MEDIUM, 15.0),# Stage1+Stage2 = 15일
            (1551, 2025, ComplexityLevel.MEDIUM, 16.0),# Stage1+Stage2 = 16일
            (2026, 2675, ComplexityLevel.MEDIUM, 17.0),# Stage1+Stage2 = 17일
            (2676, 3500, ComplexityLevel.MEDIUM, 18.0),# Stage1+Stage2 = 18일
            (3501, 4625, ComplexityLevel.MEDIUM, 19.0),# Stage1+Stage2 = 19일
            (4626, 6100, ComplexityLevel.MEDIUM, 20.0),# Stage1+Stage2 = 20일
            (6101, 8075, ComplexityLevel.MEDIUM, 21.0),# Stage1+Stage2 = 21일
            (8076, 10700, ComplexityLevel.MEDIUM, 22.0),# Stage1+Stage2 = 22일
            (10701, 14200, ComplexityLevel.MEDIUM, 23.0),# Stage1+Stage2 = 23일
            (14201, 18800, ComplexityLevel.MEDIUM, 24.0),# Stage1+Stage2 = 24일
            (18801, 25000, ComplexityLevel.MEDIUM, 25.0),# Stage1+Stage2 = 25일
            
            # Low complexity (OH&SMS) - ENP 426-625: 9일
            (426, 625, ComplexityLevel.LOW, 9.0),     # Stage1+Stage2 = 9일
            (626, 875, ComplexityLevel.LOW, 10.0),    # Stage1+Stage2 = 10일
            (876, 1175, ComplexityLevel.LOW, 11.0),   # Stage1+Stage2 = 11일
            (1176, 1550, ComplexityLevel.LOW, 12.0),  # Stage1+Stage2 = 12일
            (1551, 2025, ComplexityLevel.LOW, 13.0),  # Stage1+Stage2 = 13일
            (2026, 2675, ComplexityLevel.LOW, 14.0),  # Stage1+Stage2 = 14일
            (2676, 3500, ComplexityLevel.LOW, 15.0),  # Stage1+Stage2 = 15일
            (3501, 4625, ComplexityLevel.LOW, 16.0),  # Stage1+Stage2 = 16일
            (4626, 6100, ComplexityLevel.LOW, 17.0),  # Stage1+Stage2 = 17일
            (6101, 8075, ComplexityLevel.LOW, 18.0),  # Stage1+Stage2 = 18일
            (8076, 10700, ComplexityLevel.LOW, 19.0), # Stage1+Stage2 = 19일
            (10701, 14200, ComplexityLevel.LOW, 20.0),# Stage1+Stage2 = 20일
            (14201, 18800, ComplexityLevel.LOW, 21.0),# Stage1+Stage2 = 21일
            (18801, 25000, ComplexityLevel.LOW, 22.0),# Stage1+Stage2 = 22일
        ]
        
        # 모든 표준별 테이블 데이터를 통합
        all_data = []
        
        # QMS 데이터 추가 (표준 타입 정보 포함)
        for enp_min, enp_max, complexity, total_stage_days in qms_data:
            all_data.append((enp_min, enp_max, complexity, total_stage_days, StandardType.ISO9001))
        
        # EMS 데이터 추가 (표준 타입 정보 포함)
        for enp_min, enp_max, complexity, total_stage_days in ems_data:
            all_data.append((enp_min, enp_max, complexity, total_stage_days, StandardType.ISO14001))
        
        # OH&SMS 데이터 추가 (표준 타입 정보 포함)
        for enp_min, enp_max, complexity, total_stage_days in ohsms_data:
            all_data.append((enp_min, enp_max, complexity, total_stage_days, StandardType.ISO45001))
        
        for enp_min, enp_max, complexity, total_stage_days, standard_type in all_data:
            tables.append(MandayTable(
                enp_min=enp_min,
                enp_max=enp_max,
                complexity=complexity,
                stage2_days=total_stage_days,
                standard_type=standard_type
            ))
        
        return tables
    
    def get_stage2_days(self, enp: int, complexity: ComplexityLevel, standard: StandardType) -> float:
        """ENP, 복잡도, 표준에 따른 Stage1+Stage2 총합 일수 조회 (IAF MD5 표준)"""
        for table in self.tables:
            if (table.enp_min <= enp <= table.enp_max and 
                table.complexity == complexity and
                table.standard_type == standard):
                return table.stage2_days
        
        # 범위를 벗어나는 경우 가장 가까운 값 사용
        if enp < 1:
            return self._get_min_days(complexity, standard)
        else:
            return self._get_max_days(complexity, standard)
    
    def _get_min_days(self, complexity: ComplexityLevel, standard: StandardType) -> float:
        """최소 일수 반환"""
        min_tables = [t for t in self.tables if t.complexity == complexity and t.standard_type == standard]
        if min_tables:
            return min(t.stage2_days for t in min_tables)
        return 1.0
    
    def _get_max_days(self, complexity: ComplexityLevel, standard: StandardType) -> float:
        """최대 일수 반환"""
        max_tables = [t for t in self.tables if t.complexity == complexity and t.standard_type == standard]
        if max_tables:
            return max(t.stage2_days for t in max_tables)
        return 12.5
    
    def calculate_stage_days(self, total_stage_days: float, 
                           stage1: bool = True, 
                           surveillance: bool = True, 
                           recert: bool = False) -> Dict[str, float]:
        """IAF MD5 표준: Stage1+Stage2 총합에서 각 단계 일수 계산 (0.5일 단위 라운딩)
        
        IAF MD5 표준에 따르면:
        - Tables의 값은 Stage1+Stage2의 총합
        - Stage1과 Stage2의 비율은 표준에서 명시적으로 정의하지 않음
        - 일반적인 관행: Stage2가 Stage1보다 더 많은 시간 소요
        - 3.9조: 감소 요인의 최대값이 30% (Stage1 비율이 아님)
        """
        days = {}
        
        if stage1:
            # IAF MD5 표준 해석: Stage1은 일반적으로 Stage2보다 적은 시간 소요
            # 실무적 관행에 따라 Stage1 = 40%, Stage2 = 60%로 설정
            stage1_calc = total_stage_days * 0.4
            days['stage1'] = self.round_to_half_day(stage1_calc)
            
            # Stage2 = 나머지 (60%)
            stage2_calc = total_stage_days * 0.6
            days['stage2'] = self.round_to_half_day(stage2_calc)
        else:
            days['stage1'] = 0.0
            days['stage2'] = total_stage_days  # Stage1이 없으면 전체가 Stage2
        
        if surveillance:
            # IAF MD5: Surveillance = (Stage1+Stage2) × 1/3 (약 33%), 소수점 둘째자리까지 계산 후 0.5일 단위로 라운딩
            surveillance_calc = total_stage_days * (1/3)
            days['surveillance'] = self.round_to_half_day(surveillance_calc)
        else:
            days['surveillance'] = 0.0
            
        if recert:
            # IAF MD5: Recert = (Stage1+Stage2) × 2/3 (약 67%), 소수점 둘째자리까지 계산 후 0.5일 단위로 라운딩
            recert_calc = total_stage_days * (2/3)
            days['recert'] = self.round_to_half_day(recert_calc)
        else:
            days['recert'] = 0.0
            
        return days
    
    def round_to_half_day(self, days: float) -> float:
        """0.5일 단위로 라운딩 (사사오입 방식)"""
        # 소수점 둘째자리까지 계산 후 사사오입
        rounded = round(days, 2)
        # 0.5일 단위로 반올림 (사사오입)
        return round(rounded * 2) / 2
    
    def round_to_full_day(self, days: float) -> float:
        """1일 단위로 라운딩"""
        return round(days)
    
    def get_complexity_level(self, enp: int, standard: StandardType, 
                           environmental_impact: str = "MEDIUM",
                           safety_risk: str = "MEDIUM") -> ComplexityLevel:
        """ENP와 표준별 복잡도 요인에 따른 복잡도 레벨 결정"""
        
        if standard == StandardType.ISO9001:
            # QMS: ENP 기반 복잡도 결정
            if enp <= 50:
                return ComplexityLevel.SMALL
            elif enp <= 200:
                return ComplexityLevel.MEDIUM
            else:
                return ComplexityLevel.LARGE
                
        elif standard == StandardType.ISO14001:
            # EMS: 환경 영향도 기반 복잡도 결정
            if environmental_impact == "HIGH":
                return ComplexityLevel.HIGH
            elif environmental_impact == "MEDIUM":
                return ComplexityLevel.MEDIUM
            elif environmental_impact == "LOW":
                return ComplexityLevel.LOW
            else:  # LIMITED
                return ComplexityLevel.LIMITED
                
        elif standard == StandardType.ISO45001:
            # OH&SMS: 안전보건 위험도 기반 복잡도 결정
            if safety_risk == "HIGH":
                return ComplexityLevel.HIGH
            elif safety_risk == "MEDIUM":
                return ComplexityLevel.MEDIUM
            else:  # LOW
                return ComplexityLevel.LOW
                
        else:
            # 기타 표준: 기본 ENP 기반
            if enp <= 50:
                return ComplexityLevel.SMALL
            elif enp <= 200:
                return ComplexityLevel.MEDIUM
            else:
                return ComplexityLevel.LARGE


# 전역 인스턴스
manday_manager = MandayTableManager()
