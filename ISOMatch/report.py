#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
회사명/홈페이지 입력 → 공시·뉴스·SNS·리스크 요약 리포트
+ HTML 렌더링 + PDF 자동 생성

- 한국 공시: dart-fss (환경변수 DART_API_KEY)
- 미국 공시: sec-api (환경변수 SEC_API_KEY, 없으면 해당 파트 생략)
- 뉴스: feedparser + newspaper3k
- SNS: snscrape (X/트위터)
- 리스크: FinBERT 감성 + 키워드 룰
- PDF: WeasyPrint(우선) → 실패 시 ReportLab로 폴백
"""

import os, re, json, argparse, datetime as dt, time
from pathlib import Path
from typing import List, Dict, Any, Optional
import base64
from io import BytesIO
import hashlib
import pickle

# ---- Core deps
import tldextract, feedparser, requests
from newspaper import Article
import tweepy
try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_AVAILABLE = True
except Exception:
    SNSCRAPE_AVAILABLE = False
from bs4 import BeautifulSoup

# 환경변수 자동 로딩 (.env)
try:
	from dotenv import load_dotenv
	load_dotenv()
except Exception:
	pass

USER_AGENT = os.getenv("SEC_USER_AGENT") or "ISOMatch/1.0 (neod7305@gmail.com)"

def _fetch_edgar_filings_fallback(cik: str, form_types: Optional[List[str]], limit: int, from_date: Optional[str], to_date: Optional[str]) -> List[Dict[str, Any]]:
	"""EDGAR submissions API 폴백 수집. cik는 숫자 10자리로 패딩해야 함."""
	clean_cik = str(cik).lstrip('0')
	try:
		cik_int = int(clean_cik)
	except Exception:
		return []
	padded = f"{cik_int:010d}"
	url = f"https://data.sec.gov/submissions/CIK{padded}.json"
	headers = {"User-Agent": USER_AGENT}
	resp = requests.get(url, headers=headers, timeout=30)
	if resp.status_code != 200:
		return []
	js = resp.json()
	filings = (js.get('filings') or {}).get('recent') or {}
	forms = filings.get('form') or []
	dates = filings.get('filingDate') or []
	accessions = filings.get('accessionNumber') or []
	primary_docs = filings.get('primaryDocument') or []
	companies = js.get('name') or ""
	results: List[Dict[str, Any]] = []
	for i in range(min(len(forms), len(dates), len(accessions), len(primary_docs))):
		form = (forms[i] or '').strip()
		if form_types and form not in set(form_types):
			continue
		filing_date = (dates[i] or '').strip()
		if from_date and filing_date and filing_date < from_date:
			continue
		if to_date and filing_date and filing_date > to_date:
			continue
		acc = (accessions[i] or '').replace('-', '')
		doc = primary_docs[i] or ''
		filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc}/{doc}"
		results.append({
			"title": form,
			"date": filing_date,
			"cik": padded,
			"company": companies,
			"type": form,
			"source": "SEC",
			"url": filing_url,
		})
		if len(results) >= max(1, limit):
			break
	return results

def _fetch_edgar_atom_fallback(cik: str, form_types: Optional[List[str]], limit: int, from_date: Optional[str], to_date: Optional[str]) -> List[Dict[str, Any]]:
	"""EDGAR browse-edgar Atom 피드 폴백."""
	clean_cik = str(cik).lstrip('0')
	try:
		cik_int = int(clean_cik)
	except Exception:
		return []

def _fetch_sec_search_index(query_str: str, limit: int) -> List[Dict[str, Any]]:
	"""SEC 공식 Search Index API 폴백 (efts.sec.gov)."""
	url = "https://efts.sec.gov/LATEST/search-index"
	headers = {"User-Agent": USER_AGENT, "Accept": "application/json", "Content-Type": "application/json"}
	payload = {
		"query": {"query_string": {"query": query_str}},
		"from": 0,
		"size": limit,
		"sort": [{"filedAt": {"order": "desc"}}],
	}
	try:
		resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
		if resp.status_code != 200:
			return []
		js = resp.json() or {}
		hits = (js.get("hits") or {}).get("hits") or []
		out: List[Dict[str, Any]] = []
		for h in hits:
			src = (h or {}).get("_source") or {}
			title = src.get("formType")
			company = src.get("companyName")
			if not (title and company):
				continue
			out.append({
				"title": title,
				"date": (src.get("filedAt") or "")[:10],
				"cik": src.get("cik") or src.get("ciks") or None,
				"company": company,
				"type": title,
				"source": "SEC",
				"url": src.get("linkToFilingDetails") or src.get("linkToHtml") or None,
			})
		return out
	except Exception:
		return []
	padded = f"{cik_int:010d}"
	url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={padded}&owner=exclude&count=100&output=atom"
	headers = {"User-Agent": USER_AGENT}
	try:
		resp = requests.get(url, headers=headers, timeout=30)
		if resp.status_code != 200:
			return []
		feed = feedparser.parse(resp.text)
		items: List[Dict[str, Any]] = []
		for e in getattr(feed, 'entries', [])[:200]:
			title = getattr(e, 'title', '') or ''
			link = getattr(e, 'link', '') or ''
			published = getattr(e, 'published', '') or ''
			form = ''
			# 제목에 폼타입이 포함되는 형식: "Form 6-K ..." 또는 "6-K ..."
			for cand in (form_types or []):
				if cand and cand in title:
					form = cand
					break
			if form_types and not form:
				# 폼 필터가 있는 경우 매칭 실패 시 스킵
				continue
			# 날짜 필터
			date_ymd = (published or '')[:10]
			if from_date and date_ymd and date_ymd < from_date:
				continue
			if to_date and date_ymd and date_ymd > to_date:
				continue
			items.append({
				"title": form or title,
				"date": date_ymd,
				"cik": padded,
				"company": "",
				"type": form or title,
				"source": "SEC",
				"url": link,
			})
			if len(items) >= max(1, limit):
				break
		return items
	except Exception:
		return []

# ---- NLP / Risk
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ---- ISO 31000 Risk Management (제거됨)

# ---- ChatGPT Enhanced Analysis
try:
    from chatgpt_enhanced_analyzer import ChatGPTEnhancedAnalyzer
    CHATGPT_AVAILABLE = True
    # ✅ 보안 강화: 환경변수에서 API 키 로드
    CHATGPT_API_KEY = os.getenv("OPENAI_API_KEY")
    if not CHATGPT_API_KEY:
        print("⚠️ WARNING: OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("ChatGPT 분석 기능이 비활성화됩니다.")
        CHATGPT_AVAILABLE = False
except Exception:
    CHATGPT_AVAILABLE = False
    CHATGPT_API_KEY = None

# ---- Charts
import matplotlib.pyplot as plt

# ---- HTML Templating
from jinja2 import Template

# ---- PDF backends (WeasyPrint first, then ReportLab)
WEASYPRINT_AVAILABLE = True
try:
    from weasyprint import HTML, CSS
except Exception:
    WEASYPRINT_AVAILABLE = False

REPORTLAB_AVAILABLE = True
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
except Exception:
    REPORTLAB_AVAILABLE = False

# ---- DART (KR)
try:
    import dart_fss as dart
    DART_AVAILABLE = True
except Exception:
    DART_AVAILABLE = False

SEC_API_QUERY_URL = "https://api.sec-api.io/query"
SEC_API_FILINGS_URL = "https://api.sec-api.io/filings"
SERPAPI_BASE_URL = "https://serpapi.com/search.json"
DATA_DIR = Path("data"); DATA_DIR.mkdir(exist_ok=True)
REPORT_DIR = Path("reports"); REPORT_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path("cache"); CACHE_DIR.mkdir(exist_ok=True)
CACHE_EXPIRY = 3600  # 1시간

RISK_KEYWORDS = [
    # 기존 키워드
    r"리콜|recall",
    r"소송|lawsuit|litigation|class action",
    r"해킹|유출|breach|hack|data leak|ransom",
    r"제재|sanction|embargo",
    r"회계\s?부정|fraud|accounting scandal",
    r"규제\s?위반|non-?compliance|violation",
    
    # 재무/경영 리스크
    r"폐업|bankruptcy|insolvency|파산",
    r"주가\s?하락|stock\s?decline|market\s?crash|주가폭락",
    r"손실|loss|deficit|적자",
    r"부채|debt|liability|채무",
    r"유동성\s?위기|liquidity\s?crisis|자금난",
    r"인수합병|M&A|merger|acquisition|합병",
    
    # 경영진/조직 리스크
    r"경영진\s?교체|CEO\s?change|management\s?shakeup|사장교체",
    r"이사회\s?해임|board\s?dismissal|이사해임",
    r"내부\s?고발|whistleblower|내부신고",
    r"파업|strike|노사갈등|labor\s?dispute",
    r"조직\s?개편|restructuring|reorganization|구조조정",
    
    # 제품/서비스 리스크
    r"품질\s?문제|quality\s?issue|불량품",
    r"안전\s?사고|safety\s?accident|사고",
    r"환경\s?문제|environmental|pollution|오염",
    r"건강\s?위험|health\s?risk|건강피해",
    r"서비스\s?중단|service\s?outage|장애",
    
    # 규제/법적 리스크
    r"법적\s?분쟁|legal\s?dispute|법적갈등",
    r"반독점|antitrust|monopoly|독점규제",
    r"세금\s?문제|tax\s?issue|세무조사",
    r"허가\s?취소|license\s?revocation|인허가취소",
    r"정부\s?조사|government\s?investigation|공권력조사",
    
    # 시장/경쟁 리스크
    r"시장\s?점유율\s?하락|market\s?share\s?decline|점유율하락",
    r"경쟁사\s?대응|competitor\s?response|경쟁대응",
    r"원자재\s?가격\s?상승|raw\s?material\s?price|원료가격",
    r"환율\s?변동|exchange\s?rate|환율리스크",
    r"경기\s?침체|recession|경기하락",
    
    # 기술/보안 리스크
    r"시스템\s?장애|system\s?failure|시스템오류",
    r"네트워크\s?보안|network\s?security|보안위협",
    r"개인정보\s?유출|personal\s?data\s?leak|개인정보침해",
    r"지적재산권|intellectual\s?property|특허분쟁",
    r"기술\s?도태|technology\s?obsolescence|기술낙후",
    
    # 브랜드/평판 리스크
    r"브랜드\s?이미지\s?손상|brand\s?damage|브랜드손상",
    r"고객\s?불만|customer\s?complaint|고객민원",
    r"소셜미디어\s?위기|social\s?media\s?crisis|SNS위기",
    r"보이콧|boycott|불매운동",
    r"평판\s?하락|reputation\s?decline|이미지하락",
    
    # 공급망/물류 리스크
    r"공급망\s?중단|supply\s?chain\s?disruption|공급중단",
    r"물류\s?지연|logistics\s?delay|배송지연",
    r"공급업체\s?문제|supplier\s?issue|협력사문제",
    r"재고\s?부족|inventory\s?shortage|재고부족",
    r"운송\s?사고|transportation\s?accident|운송사고",
    
    # 국제/정치 리스크
    r"무역\s?분쟁|trade\s?dispute|무역갈등",
    r"정치적\s?불안정|political\s?instability|정치불안",
    r"국제\s?분쟁|international\s?conflict|국제갈등",
    r"테러|terrorism|테러위협",
    r"자연재해|natural\s?disaster|천재지변"
]

def now_utc_iso(): return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
def sanitize_filename(name: str) -> str: return re.sub(r"[^a-zA-Z0-9가-힣_.-]+", "_", name)[:80]

def extract_domain(url_or_name: str) -> Optional[str]:
    if not url_or_name: return None
    if "http" in url_or_name or "." in url_or_name:
        ext = tldextract.extract(url_or_name)
        if ext.domain and ext.suffix: return f"{ext.domain}.{ext.suffix}"
    return None

def save_json(obj: Any, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

# ---------------------------
# Identify
# ---------------------------
def identify_company(company_name: Optional[str], url: Optional[str]) -> Dict[str, Any]:
    return {"name": company_name, "domain": extract_domain(url or "")}

# ---------------------------
# Filings
# ---------------------------
def fetch_dart_filings(company_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """DART에서 한국 기업 공시 정보 수집 (강화된 버전)"""
    if not DART_AVAILABLE: 
        print(f"[WARN] DART 시스템을 사용할 수 없습니다: {company_name}")
        return []
    
    api_key = os.getenv("DART_API_KEY")
    if not api_key: 
        print(f"[WARN] DART API 키가 설정되지 않았습니다: {company_name}")
        return []
    
    try:
        dart.set_api_key(api_key=api_key)
    except Exception:
        # 구버전/신버전 호환
        try:
            from dart_fss import set_api_key as _legacy_set
            _legacy_set(api_key)
        except Exception:
            pass
    
    try:
        print(f"🔍 DART에서 {company_name} 공시 정보 수집 중...")
        
        # 기업 목록 조회 (재시도 로직 포함)
        corp_list = None
        for attempt in range(3):
            try:
                # 최신 dart-fss는 get_corp_list(), 일부 구버전은 corp.get_corp_list()
                try:
                    corp_list = dart.get_corp_list()
                except Exception:
                    corp_list = dart.corp.get_corp_list()
                break
            except Exception as e:
                if attempt < 2:
                    print(f"[WARN] DART 기업 목록 조회 재시도 {attempt + 1}/3: {e}")
                    time.sleep(2)
                else:
                    raise e
        
        if not corp_list:
            print(f"❌ DART 기업 목록을 가져올 수 없습니다: {company_name}")
            return []
        
        # 기업 검색 (정확한 이름 우선, 유사한 이름 차선)
        result = corp_list.find_by_corp_name(company_name, exactly=True)
        if not result:
            result = corp_list.find_by_corp_name(company_name, exactly=False)
            if result:
                print(f"ℹ️  정확한 이름으로 찾지 못해 유사한 이름으로 검색: {company_name}")
        
        if not result:
            print(f"[WARN] DART에서 {company_name}을 찾을 수 없습니다")
            return []
        
        corp_obj = result[0]
        corp_code = corp_obj.corp_code
        print(f"[OK] {company_name} 기업 코드 발견: {corp_code}")
        
        # 공시 목록 조회 (search_filings 사용 - 정확한 API)
        resp = None
        try:
            # 최근 1년간 공시 조회
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            api = getattr(dart, 'api', None)
            if api and hasattr(api, 'filings') and hasattr(api.filings, 'search_filings'):
                resp = api.filings.search_filings(
                    corp_code=corp_code,
                    bgn_de=start_date,
                    end_de=end_date,
                    page_no=1,
                    page_count=min(limit, 100)
                )
        except Exception as e:
            print(f"[DEBUG] DART API 호출 오류: {e}")
            resp = None

        out = []
        if isinstance(resp, dict) and resp.get('list'):
            for it in resp['list']:
                out.append({
                    "title": it.get('report_nm'),
                    "date": it.get('rcept_dt'),
                    "rcp_no": it.get('rcept_no'),
                    "corp_name": it.get('corp_name'),
                    "corp_code": corp_code,
                    "type": it.get('report_nm'),
                    "source": "DART",
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={it.get('rcept_no')}"
                })
        else:
            # 대체 경로: filings.search 사용 시 구조 맞추기
            try:
                from dart_fss.filings.search import search as filings_search
                search_result = filings_search(corp_code=corp_code)
                items = getattr(search_result, 'report_list', []) or []
                for r in items:
                    out.append({
                        "title": getattr(r, 'report_nm', None),
                        "date": getattr(r, 'rcept_dt', None),
                        "rcp_no": getattr(r, 'rcept_no', None),
                        "corp_name": getattr(r, 'corp_name', None),
                        "corp_code": corp_code,
                        "type": getattr(r, 'report_nm', None),
                        "source": "DART",
                        "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={getattr(r, 'rcept_no', '')}"
                    })
            except Exception:
                pass
        
        print(f"[OK] DART에서 {len(out)}건의 공시 정보 수집 완료: {company_name}")
        return out[:limit]
        
    except Exception as e:
        error_msg = f"DART fetch failed for {company_name}: {str(e)}"
        print(f"❌ {error_msg}")
        return [{"error": error_msg, "company": company_name, "source": "DART"}]

def fetch_sec_filings_by_name(
    company_name: str,
    limit: int = 10,
    ticker: Optional[str] = None,
    cik: Optional[str] = None,
    form_types: Optional[List[str]] = None,
    from_date: Optional[str] = None,  # YYYY-MM-DD
    to_date: Optional[str] = None     # YYYY-MM-DD
) -> List[Dict[str, Any]]:
    """SEC에서 미국 기업 공시 정보 수집 (강화된 버전)"""
    api_key = os.getenv("SEC_API_KEY")
    if not api_key: 
        print(f"[WARN] SEC API 키가 설정되지 않았습니다: {company_name}")
        return []
    
    try:
        print(f"🔍 SEC에서 {company_name} 공시 정보 수집 중...")
        
        # 1) EDGAR 우선 수집 (Search Index → Submissions → Atom)
        primary_out: List[Dict[str, Any]] = []
        try:
            primary_out = _fetch_sec_search_index(query_str=query_str, limit=limit) or []
        except Exception:
            primary_out = []
        if not primary_out and cik:
            try:
                primary_out = _fetch_edgar_filings_fallback(cik=cik, form_types=form_types, limit=limit, from_date=from_date, to_date=to_date) or []
            except Exception:
                primary_out = []
            if not primary_out:
                try:
                    primary_out = _fetch_edgar_atom_fallback(cik=cik, form_types=form_types, limit=limit, from_date=from_date, to_date=to_date) or []
                except Exception:
                    primary_out = []
        if primary_out:
            return primary_out[:limit]

        # 2) SEC-API 시도
        url = SEC_API_QUERY_URL
        # 쿼리 문자열 구성
        query_parts = []
        if ticker:
            query_parts.append(f"ticker:{ticker}")
        if cik:
            query_parts.append(f"cik:{cik}")
        if company_name:
            query_parts.append(company_name)
        if form_types:
            types_or = " OR ".join([f"formType:{t}" for t in form_types])
            query_parts.append(f"({types_or})")
        if from_date or to_date:
            start = from_date or "1900-01-01"
            end = to_date or "2100-12-31"
            query_parts.append(f"filedAt:[{start} TO {end}]")
        query_str = " AND ".join([p for p in query_parts if p]) or company_name

        payload = {
            "query": {"query_string": {"query": query_str}},
            "from": 0, "size": limit,
            "sort": [{"filedAt": {"order": "desc"}}]
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # 재시도 로직 포함
        resp = None
        for attempt in range(3):
            try:
                resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
                resp.raise_for_status()
                break
            except requests.exceptions.Timeout:
                if attempt < 2:
                    print(f"[WARN] SEC API 타임아웃, 재시도 {attempt + 1}/3: {company_name}")
                    time.sleep(3)
                else:
                    raise Exception(f"SEC API 타임아웃 (3회 시도 실패): {company_name}")
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    print(f"[WARN] SEC API 요청 오류, 재시도 {attempt + 1}/3: {e}")
                    time.sleep(2)
                else:
                    print(f"[WARN] SEC API 요청 실패(최종): {e} — 폴백 엔드포인트 시도")
                    resp = None
                    break
        
        data = None
        if resp and resp.status_code == 200:
            data = resp.json()
        else:
            # Fallback: GET with token/query params
            try:
                params = {
                    "token": api_key,
                    "apiKey": api_key,
                    "query": json.dumps({"query_string": {"query": query_str}}),
                    "from": 0,
                    "size": limit,
                    "sort": "filedAt:desc"
                }
                # 추가 필드 직접 전달 시도 (엔드포인트 호환용)
                if cik:
                    params["cik"] = cik
                if ticker:
                    params["ticker"] = ticker
                if form_types:
                    params["formType"] = ",".join(form_types)
                if from_date:
                    params["from"] = from_date
                if to_date:
                    params["to"] = to_date
                resp2 = requests.get(SEC_API_FILINGS_URL, params=params, timeout=30)
                resp2.raise_for_status()
                data = resp2.json()
            except Exception as _:
                pass
        
        if not data:
            # SEC-API가 응답을 주지 않는 경우: EDGAR 폴백 시도
            if cik:
                try:
                    fb = _fetch_edgar_filings_fallback(cik=cik, form_types=form_types, limit=limit, from_date=from_date, to_date=to_date)
                    if fb:
                        return fb[:limit]
                except Exception:
                    pass
            print("[WARN] SEC API 응답 없음 — EDGAR 폴백도 결과 없음")
            return []
        
        # 응답 데이터 파싱 (여러 스키마 호환)
        out = []
        def _append_item(item: dict):
            title = item.get("formType") or item.get("form_type") or item.get("form")
            company = item.get("companyName") or item.get("company_name") or item.get("company")
            if not (title and company):
                return
            filed = item.get("filedAt") or item.get("filingDate") or item.get("filed_at") or ""
            url = item.get("linkToFilingDetails") or item.get("linkToHtml") or item.get("linkToFiling") or item.get("url")
            out.append({
                "title": title,
                "date": (filed or "")[:10],
                "cik": item.get("cik"),
                "company": company,
                "type": title,
                "source": "SEC",
                "url": url,
            })

        if isinstance(data, dict):
            if "hits" in data and isinstance(data["hits"], list):
                for hit in data["hits"]:
                    if isinstance(hit, dict):
                        _append_item(hit)
            elif "filings" in data and isinstance(data["filings"], list):
                for it in data["filings"]:
                    if isinstance(it, dict):
                        _append_item(it)
            elif "data" in data and isinstance(data["data"], list):
                for it in data["data"]:
                    if isinstance(it, dict):
                        _append_item(it)
            else:
                print(f"[WARN] SEC API 응답 스키마 인식 불가: {list(data.keys())}")
        elif isinstance(data, list):
            for it in data:
                if isinstance(it, dict):
                    _append_item(it)

        # 폴백: EDGAR submissions API (CIK 필요)
        if (not out) and cik:
            try:
                out = _fetch_edgar_filings_fallback(cik=cik, form_types=form_types, limit=limit, from_date=from_date, to_date=to_date)
            except Exception as _:
                out = []
            if not out:
                try:
                    out = _fetch_edgar_atom_fallback(cik=cik, form_types=form_types, limit=limit, from_date=from_date, to_date=to_date)
                except Exception:
                    out = []
        # 최종 폴백: 공식 Search Index API
        if not out:
            out = _fetch_sec_search_index(query_str=query_str, limit=limit)
        
        print(f"[OK] SEC에서 {len(out)}건의 공시 정보 수집 완료: {company_name}")
        return out[:limit]
        
    except Exception as e:
        error_msg = f"SEC fetch failed for {company_name}: {str(e)}"
        print(f"❌ {error_msg}")
        return [{"error": error_msg, "company": company_name, "source": "SEC"}]

# ---------------------------
# News
# ---------------------------
def fetch_news(company_query: str, lang: str = "ko", days: int = 14, limit: int = 8) -> List[Dict[str, Any]]:
    q = f"{company_query} when:{days}d"
    rss = f"https://news.google.com/rss/search?q={requests.utils.quote(q)}&hl={lang}"
    feed = feedparser.parse(rss)
    results = []
    for entry in feed.entries[: limit * 2]:
        link, title = entry.link, entry.title
        published = getattr(entry, "published", "")[:16]
        # 본문 추출
        text = ""
        try:
            art = Article(link); art.download(); art.parse()
            text = (art.text or "").strip()
        except Exception:
            pass
        if not text and title: text = title
        if title or text:
            results.append({
                "title": title, "url": link, "published": published,
                "excerpt": text[:800].replace("\n", " ")
            })
        if len(results) >= limit: break
    return results

# ---------------------------
# SerpApi Adapters
# ---------------------------
def _serpapi_get(params: Dict[str, Any], api_key: Optional[str]) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None
    
    # 캐시 키 생성
    cache_key = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
    cached_data = _get_cached_data(cache_key)
    if cached_data:
        return cached_data
    
    try:
        p = dict(params or {})
        p["api_key"] = api_key
        resp = requests.get(SERPAPI_BASE_URL, params=p, timeout=30)
        if resp.status_code != 200:
            return None
        data = resp.json()
        
        # 성공한 데이터를 캐시에 저장
        _save_cached_data(cache_key, data)
        return data
    except Exception:
        return None

def _get_cached_data(cache_key: str) -> Optional[Dict[str, Any]]:
    """캐시된 데이터 조회"""
    cache_file = CACHE_DIR / f"{cache_key}.pkl"
    if cache_file.exists():
        if time.time() - cache_file.stat().st_mtime < CACHE_EXPIRY:
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
    return None

def _save_cached_data(cache_key: str, data: Dict[str, Any]):
    """데이터를 캐시에 저장"""
    try:
        cache_file = CACHE_DIR / f"{cache_key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except Exception:
        pass

def build_alias_queries(company_name: Optional[str], domain: Optional[str]) -> List[str]:
    """회사명/도메인 기반 동의어 OR 쿼리 생성"""
    aliases: set = set()
    if company_name:
        aliases.add(company_name)
        aliases.add(f"{company_name} Inc")
        aliases.add(f"{company_name} Inc.")
    if domain:
        label = (domain or '').split('.') [0]
        if label and label.lower() not in {"www", "m"}:
            aliases.add(label)
    expanded = [a.strip() for a in aliases if a and len(a.strip()) > 1]
    if not expanded and company_name:
        expanded = [company_name]
    or_query = " OR ".join([f'"{a}"' for a in sorted(expanded)])
    return [or_query]

def fetch_news_serpapi(query: str, lang: str, days: int, limit: int, api_key: Optional[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
    data = _serpapi_get({
        "engine": "google_news",
        "q": f"{query} when:{days}d",
        "hl": lang or "ko",
        "num": limit,
        **({"location": location} if location else {})
    }, api_key)
    if not data:
        return []
    items = data.get("news_results", []) or []
    out: List[Dict[str, Any]] = []
    for it in items[:limit]:
        out.append({
            "title": it.get("title"),
            "url": it.get("link") or it.get("url"),
            "published": it.get("date"),
            "excerpt": it.get("snippet") or it.get("content") or "",
            "source": (it.get("source") or {}).get("name") if isinstance(it.get("source"), dict) else it.get("source"),
        })
        
    return out

def fetch_trends_serpapi(query: str, api_key: Optional[str], geo: str = "KR") -> Dict[str, Any]:
    data = _serpapi_get({
        "engine": "google_trends",
        "q": query,
        "geo": geo
    }, api_key)
    return data or {}

def fetch_patents_serpapi(query: str, api_key: str, limit: int = 10) -> Dict[str, Any]:
    """SerpApi를 통한 특허 데이터 수집 (건설업 특화)"""
    try:
        # 건설업 관련 키워드로 검색 쿼리 개선
        construction_keywords = "construction OR building OR infrastructure OR engineering OR architecture OR project OR concrete OR steel OR foundation OR structure"
        enhanced_query = f'"{query}" ({construction_keywords})'
        
        params = {
            "engine": "google_patents",
            "q": enhanced_query,
            "num": limit
        }
        
        data = _serpapi_get(params, api_key)
        if not data:
            return {"error": "특허 데이터 수집 실패"}
        
        # 결과가 너무 적으면 원래 쿼리로 재시도
        if len(data.get("patents", [])) < 3:
            fallback_params = {
                "engine": "google_patents",
                "q": f'"{query}"',
                "num": limit
            }
            data = _serpapi_get(fallback_params, api_key)
            if not data:
                return {"error": "특허 데이터 수집 실패"}
        
        patents = []
        for patent in data.get("patents", [])[:limit]:
            # 건설업 관련성 필터링 (제목에 건설 관련 키워드가 있는 경우 우선)
            title = patent.get("title", "").lower()
            if any(keyword in title for keyword in ["construction", "building", "infrastructure", "engineering", "concrete", "steel", "foundation"]):
                relevance_score = "높음"
            else:
                relevance_score = "보통"
            
            patents.append({
                "title": patent.get("title", "제목 없음"),
                "summary": patent.get("summary", "요약 없음"),
                "patent_number": patent.get("patent_number", ""),
                "filing_date": patent.get("filing_date", ""),
                "relevance": relevance_score
            })
        
        return {"patents": patents, "total": len(patents)}
        
    except Exception as e:
        return {"error": f"특허 데이터 수집 중 오류: {str(e)}"}

def fetch_ai_overview_serpapi(query: str, lang: str, api_key: Optional[str], location: Optional[str] = None) -> Dict[str, Any]:
    data = _serpapi_get({
        "engine": "google",
        "q": query,
        "hl": lang or "ko",
        **({"location": location} if location else {})
    }, api_key)
    if not data:
        return {}
    
    # AI Overview가 있으면 사용, 없으면 organic_results의 첫 번째 결과 요약 사용
    ai_overview = data.get("ai_overview")
    if ai_overview:
        return ai_overview
    
    # 폴백: 일반 검색 결과 요약
    organic = data.get("organic_results", [])
    if organic:
        first_result = organic[0]
        return {
            "summary": first_result.get("snippet", ""),
            "title": first_result.get("title", ""),
            "link": first_result.get("link", ""),
            "source": "Google 검색 결과 요약"
        }
    
    # 최종 폴백: 기본 정보
    return {
        "summary": f"{query}에 대한 최신 정보를 수집 중입니다.",
        "title": f"{query} 정보",
        "source": "기본 정보"
    }

def fetch_related_questions_serpapi(query: str, lang: str, api_key: Optional[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
    # Google 검색에서 PAA 데이터 수집 시도
    data = _serpapi_get({
        "engine": "google",
        "q": query,
        "hl": lang or "ko",
        **({"location": location} if location else {})
    }, api_key)
    
    # PAA 데이터가 있으면 사용
    if data and data.get("related_questions"):
        items = data.get("related_questions", [])
        out: List[Dict[str, Any]] = []
        for it in items:
            out.append({
                "question": it.get("question"),
                "snippet": it.get("snippet"),
                "link": it.get("link")
            })
        return out
    
    # PAA가 없으면 관련 검색어 제안으로 대체
    related_queries = [
        f"{query} 주가 전망",
        f"{query} 실적 분석",
        f"{query} 최신 뉴스",
        f"{query} 프로젝트 현황",
        f"{query} 리스크 분석",
        f"{query} 경쟁사 동향",
        f"{query} 시장 전망",
        f"{query} 투자 가치"
    ]
    
    return [{"question": q, "snippet": "관련 검색어", "link": "#"} for q in related_queries[:8]]

def fetch_youtube_serpapi(query: str, api_key: Optional[str], lang: str = "ko", limit: int = 8) -> List[Dict[str, Any]]:
    data = _serpapi_get({
        "engine": "youtube",
        "search_query": query,
        "hl": lang or "ko",
        "num": limit
    }, api_key)
    if not data:
        return []
    items = data.get("video_results", []) or []
    out: List[Dict[str, Any]] = []
    for v in items[:limit]:
        out.append({
            "title": v.get("title"),
            "url": v.get("link") or v.get("url"),
            "views": v.get("views"),
            "published": v.get("published_date") or v.get("published_time")
        })
    return out

def fetch_naver_serpapi(query: str, api_key: Optional[str], limit: int = 10) -> List[Dict[str, Any]]:
    data = _serpapi_get({
        "engine": "naver",
        "query": query,
        "where": "news",
        "num": limit
    }, api_key)
    if not data:
        return []
    items = data.get("organic_results", []) or data.get("news_results", []) or []
    out: List[Dict[str, Any]] = []
    for it in items[:limit]:
        out.append({
            "title": it.get("title"),
            "url": it.get("link") or it.get("url"),
            "excerpt": it.get("snippet") or it.get("content")
        })
    return out

def fetch_news_serpapi_with_fallback(query: str, lang: str, days: int, limit: int, api_key: Optional[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
    """SerpApi 뉴스 수집 실패 시 RSS 폴백을 사용하는 향상된 함수"""
    serpapi_news = fetch_news_serpapi(query, lang, days, limit, api_key, location)
    if serpapi_news:
        return serpapi_news
    
    # SerpApi 실패 시 기존 RSS 사용
    print("[WARN] SerpApi 뉴스 수집 실패, RSS 폴백 사용")
    return fetch_news(query, lang, days, limit)

# ---------------------------
# Social Media (Reddit + Stocktwits)
# ---------------------------
def fetch_reddit_posts(company_query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Reddit에서 회사 관련 게시물 검색"""
    try:
        # Reddit 무료 API 사용 (인증 불필요)
        url = f"https://www.reddit.com/search.json?q={requests.utils.quote(company_query)}&sort=new&limit={limit}&t=month"
        headers = {
            'User-Agent': 'CompanyRiskAnalyzer/1.0 (Educational Research Tool)',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            posts = []
            for post in data.get('data', {}).get('children', [])[:limit]:
                post_data = post['data']
                # 한국어 관련 서브레딧 우선
                if any(lang in post_data.get('subreddit', '').lower() for lang in ['korea', 'korean', 'kr']):
                    posts.append({
                        "date": dt.datetime.fromtimestamp(post_data['created_utc']).strftime("%Y-%m-%d %H:%M"),
                        "user": post_data.get('author', 'deleted'),
                        "content": post_data['title'] + " " + (post_data.get('selftext', '')[:200]),
                        "url": f"https://reddit.com{post_data['permalink']}",
                        "source": "Reddit",
                        "subreddit": post_data.get('subreddit', ''),
                        "score": post_data.get('score', 0)
                    })
                if len(posts) >= limit: break
            
            return posts if posts else [{"error": "No relevant Reddit posts found"}]
        else:
            return [{"error": f"Reddit API failed: HTTP {response.status_code}"}]
            
    except Exception as e:
        return [{"error": f"Reddit fetch failed: {e}"}]

def fetch_stocktwits(company_query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Stocktwits에서 회사 관련 메시지 검색"""
    try:
        # Stocktwits 무료 API 사용
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{company_query}.json"
        headers = {
            'User-Agent': 'CompanyRiskAnalyzer/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            messages = []
            for msg in data.get('messages', [])[:limit]:
                messages.append({
                    "date": msg['created_at'][:16].replace('T', ' '),
                    "user": msg['user']['username'],
                    "content": msg['body'],
                    "url": f"https://stocktwits.com/message/{msg['id']}",
                    "source": "Stocktwits",
                    "sentiment": msg.get('entities', {}).get('sentiment', {}).get('basic', 'neutral')
                })
            return messages if messages else [{"error": "No Stocktwits messages found"}]
        else:
            return [{"error": f"Stocktwits API failed: HTTP {response.status_code}"}]
            
    except Exception as e:
        return [{"error": f"Stocktwits fetch failed: {e}"}]

def fetch_social_media(company_query: str, since_days: int = 14, limit: int = 30) -> List[Dict[str, Any]]:
    """Reddit과 Stocktwits에서 소셜미디어 데이터 수집"""
    all_posts = []
    
    # Reddit에서 수집
    reddit_posts = fetch_reddit_posts(company_query, limit//2)
    if reddit_posts and not reddit_posts[0].get('error'):
        all_posts.extend(reddit_posts)
    
    # Stocktwits에서 수집
    stocktwits_posts = fetch_stocktwits(company_query, limit//2)
    if stocktwits_posts and not stocktwits_posts[0].get('error'):
        all_posts.extend(stocktwits_posts)
    
    # 에러가 있는 경우 빈 리스트 반환
    if not all_posts or all(all_posts[0].get('error') for post in all_posts):
        return [{"error": "Social media data collection failed"}]
    
    return all_posts[:limit]

# ---------------------------
# Tweets (X) - 기존 함수 유지 (API 키가 있는 경우)
# ---------------------------
def fetch_tweets(query: str, since_days: int = 14, limit: int = 30) -> List[Dict[str, Any]]:
    # tweepy를 사용한 트위터 검색 (API 키가 필요하지만 더 안정적)
    try:
        # 환경변수에서 API 키 확인
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            return [{"error": "Twitter API keys not configured"}]
        
        # tweepy 인증
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # 검색 쿼리 구성
        since_date = (dt.datetime.utcnow() - dt.timedelta(days=since_days)).date().strftime("%Y-%m-%d")
        search_query = f"{query} since:{since_date}"
        
        tweets = []
        for tweet in tweepy.Cursor(api.search_tweets, q=search_query, lang="ko", tweet_mode="extended").items(limit):
            tweets.append({
                "date": tweet.created_at.strftime("%Y-%m-%d %H:%M"),
                "content": tweet.full_text,
                "url": f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            })
        
        return tweets
        
    except Exception as e:
        return [{"error": f"Twitter API failed: {e}"}]

# ---------------------------
# Risk
# ---------------------------
class FinBertScorer:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def score(self, texts: List[str]) -> Dict[str, float]:
        if not texts: return {"neg": 0.0, "neu": 0.0, "pos": 0.0}
        negs, neus, poss = [], [], []
        for t in texts:
            if not t: continue
            inputs = self.tokenizer(t[:4000], truncation=True, return_tensors="pt")
            with torch.no_grad():
                probs = torch.softmax(self.model(**inputs).logits, dim=-1).squeeze().tolist()
                pos, neg, neu = probs[0], probs[1], probs[2]
                poss.append(pos); negs.append(neg); neus.append(neu)
        avg = lambda x: float(sum(x)/len(x)) if x else 0.0
        return {"neg": avg(negs), "neu": avg(neus), "pos": avg(poss)}

def keyword_hits(texts: List[str], patterns: List[str]) -> Dict[str, int]:
    bag = "\n".join([t for t in texts if t])[:20000]
    return {p: len(re.findall(p, bag, flags=re.IGNORECASE)) for p in patterns}

def simple_risk_score(finbert: Dict[str, float], hits: Dict[str, int]) -> float:
    neg = finbert.get("neg", 0.0)
    kw_total = sum(hits.values())
    kw_signal = min(1.0, (0.2 * (1 + (kw_total ** 0.5))))  # 0~1
    return round(0.6 * neg + 0.4 * kw_signal, 3)

def analyze_company_risks_baseline(data: Dict) -> Dict:
    """ISO 31000 제거 후 기본 리스크 요약 산출(FinBERT + 키워드 기반)."""
    finbert_result = data.get("risk", {}).get("finbert", {})
    keyword_hits_map = data.get("risk", {}).get("keyword_hits", {})
    total_hits = sum(keyword_hits_map.values())
    neg = float(finbert_result.get("neg", 0.0))
    # 간단 종합 점수(0~100): 부정(0~1)*70 + 키워드 신호(0~1)*30
    kw_signal = min(1.0, 0.2 * (1 + (total_hits ** 0.5)))
    integrated = (neg * 0.7 + kw_signal * 0.3) * 100.0
    return {
        "overall_score": round(100.0 - integrated, 1),  # 점수 높을수록 안전
        "finbert_analysis": finbert_result,
        "keyword_analysis": {"total_hits": total_hits, "detail": keyword_hits_map},
        "risk_level": "높음" if integrated >= 66 else ("보통" if integrated >= 33 else "낮음"),
        "assessment_method": "FinBERT + Keyword Analysis",
    }

def _get_assessment_text(score: float) -> str:
    """점수에 따른 평가 텍스트 반환"""
    if score >= 80:
        return "매우 우수"
    elif score >= 60:
        return "우수"
    elif score >= 40:
        return "보통"
    elif score >= 20:
        return "개선 필요"
    else:
        return "긴급 개선 필요"

def infer_industry(entity: Dict[str, Any], news: List[Dict[str, Any]], filings: List[Dict[str, Any]]) -> str:
    """간단한 규칙 기반 산업 추론 (ko/en 키워드 혼합)."""
    text_corpus = ' '.join([
        (entity.get('name') or ''),
        (entity.get('domain') or ''),
        ' '.join([(n.get('title') or '') + ' ' + (n.get('excerpt') or '') for n in news[:20]])
    ]).lower()
    rules = [
        ("construction|건설|infra|infrastructure|civil|토목|현장|플랜트", "construction"),
        ("semiconductor|chip|foundry|electronics|전자|반도체|디스플레이", "manufacturing"),
        ("automotive|vehicle|car|mobility|자동차|부품|모빌리티", "automotive"),
        ("energy|power|utility|전력|발전|수력|풍력|태양광|원자력|석유|가스", "energy"),
        ("bank|finance|보험|증권|금융", "finance"),
        ("hospital|clinic|제약|바이오|헬스케어|의료", "healthcare"),
        ("retail|consumer|ecommerce|리테일|유통|소매|이커머스", "retail"),
        ("software|cloud|ai|it|tech|플랫폼|소프트웨어|클라우드|테크|it", "technology"),
        ("steel|chem|material|철강|화학|소재", "manufacturing"),
    ]
    for pattern, label in rules:
        try:
            if re.search(pattern, text_corpus):
                return label
        except Exception:
            continue
    return "other"

# ✅ 실제 ISO 표준 요구사항 정의
ISO_REQUIREMENTS = {
    "9001": {
        "name": "품질경영시스템",
        "clauses": {
            "context": {
                "weight": 0.15,
                "name": "조직과 상황",
                "requirements": [
                    "조직의 내외부 이슈 파악",
                    "이해관계자 요구사항 분석", 
                    "품질경영시스템 범위 결정"
                ]
            },
            "leadership": {
                "weight": 0.20,
                "name": "리더십",
                "requirements": [
                    "최고경영자의 리더십과 의지",
                    "고객중심 문화",
                    "품질방침 수립과 전파",
                    "조직 역할과 책임 할당"
                ]
            },
            "planning": {
                "weight": 0.15,
                "name": "기획",
                "requirements": [
                    "리스크와 기회 관리",
                    "품질목표 설정과 달성 계획",
                    "변경사항 관리"
                ]
            },
            "support": {
                "weight": 0.20,
                "name": "지원",
                "requirements": [
                    "자원 확보 및 관리",
                    "역량 있는 인적자원",
                    "인식 및 소통",
                    "문서화된 정보 관리"
                ]
            },
            "operation": {
                "weight": 0.20,
                "name": "운영",
                "requirements": [
                    "운영 계획 및 관리",
                    "제품/서비스 요구사항",
                    "외부 공급자 관리",
                    "제품/서비스 제공"
                ]
            },
            "evaluation": {
                "weight": 0.10,
                "name": "평가",
                "requirements": [
                    "모니터링과 측정",
                    "고객만족도 평가",
                    "내부심사",
                    "경영검토"
                ]
            }
        }
    },
    "14001": {
        "name": "환경경영시스템", 
        "clauses": {
            "context": {
                "weight": 0.15,
                "name": "조직과 상황",
                "requirements": [
                    "환경경영시스템 범위 결정",
                    "환경 이슈와 요구사항 파악",
                    "이해관계자 요구사항"
                ]
            },
            "leadership": {
                "weight": 0.20,
                "name": "리더십",
                "requirements": [
                    "환경방침 수립과 의지",
                    "환경 책임과 권한",
                    "환경보호 약속"
                ]
            },
            "planning": {
                "weight": 0.25,
                "name": "기획",
                "requirements": [
                    "환경측면 식별과 평가",
                    "법규 및 기타 요구사항",
                    "환경목표와 달성 계획",
                    "리스크와 기회"
                ]
            },
            "support": {
                "weight": 0.15,
                "name": "지원", 
                "requirements": [
                    "자원 확보",
                    "환경 역량과 인식",
                    "소통과 참여",
                    "문서화된 정보"
                ]
            },
            "operation": {
                "weight": 0.15,
                "name": "운영",
                "requirements": [
                    "운영 관리",
                    "비상상황 대비와 대응"
                ]
            },
            "evaluation": {
                "weight": 0.10,
                "name": "평가",
                "requirements": [
                    "모니터링과 측정",
                    "법규 준수 평가",
                    "내부심사",
                    "경영검토"
                ]
            }
        }
    },
    "45001": {
        "name": "안전보건경영시스템",
        "clauses": {
            "context": {
                "weight": 0.15,
                "name": "조직과 상황",
                "requirements": [
                    "안전보건경영시스템 범위",
                    "작업환경과 이해관계자",
                    "근로자와 이해관계자 요구사항"
                ]
            },
            "leadership": {
                "weight": 0.25,
                "name": "리더십과 근로자 참여",
                "requirements": [
                    "리더십과 의지",
                    "안전보건방침",
                    "조직 역할과 책임",
                    "근로자 참여와 협의"
                ]
            },
            "planning": {
                "weight": 0.25,
                "name": "기획",
                "requirements": [
                    "위험요인과 기회",
                    "법규 및 기타 요구사항",
                    "안전보건목표와 달성 계획"
                ]
            },
            "support": {
                "weight": 0.15,
                "name": "지원",
                "requirements": [
                    "자원",
                    "역량",
                    "인식",
                    "소통",
                    "문서화된 정보"
                ]
            },
            "operation": {
                "weight": 0.15,
                "name": "운영",
                "requirements": [
                    "운영 계획과 관리",
                    "비상상황 대비와 대응"
                ]
            },
            "evaluation": {
                "weight": 0.05,
                "name": "평가",
                "requirements": [
                    "모니터링과 측정",
                    "법규 준수 평가",
                    "내부심사",
                    "경영검토"
                ]
            }
        }
    }
}

def iso_readiness_assessment_enhanced(company_data: Dict[str, Any], chatgpt_analyzer: Optional[object] = None, 
                                    lang: str = "ko", industry: Optional[str] = None, 
                                    focus_standards: Optional[List[str]] = None) -> Dict[str, Any]:
    """✅ 개선된 ISO 준비도 평가 - 실제 요구사항 기반 + ChatGPT 분석"""
    
    if not CHATGPT_AVAILABLE or not chatgpt_analyzer:
        # ChatGPT 사용 불가시 기존 방식으로 폴백
        return iso_readiness_assessment_legacy(company_data.get("keyword_hits", {}), lang, industry)
    
    # 평가할 표준 결정
    standards_to_assess = focus_standards or ["9001", "14001", "45001"]
    
    assessment_results = {}
    
    for standard in standards_to_assess:
        if standard not in ISO_REQUIREMENTS:
            continue
            
        iso_spec = ISO_REQUIREMENTS[standard]
        
        # ChatGPT를 통한 상세 평가 수행
        detailed_scores = assess_iso_standard_with_chatgpt(
            company_data, standard, iso_spec, chatgpt_analyzer, lang, industry
        )
        
        # 가중 평균으로 최종 점수 계산
        weighted_score = 0.0
        clause_details = {}
        
        for clause_id, clause_data in iso_spec["clauses"].items():
            clause_score = detailed_scores.get(clause_id, 50)  # 기본값 50점
            weighted_score += clause_score * clause_data["weight"]
            
            clause_details[clause_id] = {
                "name": clause_data["name"],
                "score": clause_score,
                "weight": clause_data["weight"],
                "requirements": clause_data["requirements"],
                "gaps": detailed_scores.get(f"{clause_id}_gaps", [])
            }
        
        # 산업별 보너스 적용
        industry_bonus = get_industry_bonus(industry, standard)
        final_score = min(100, round(weighted_score + industry_bonus, 1))
        
        # 상태 결정
        status = get_readiness_status(final_score, lang)
        
        assessment_results[standard] = {
            "readiness_score": final_score,
            "status": status,
            "standard_name": iso_spec["name"],
            "clause_details": clause_details,
            "industry_bonus": industry_bonus,
            "assessment_method": "ChatGPT Enhanced Analysis"
        }
    
    # 전체 점수 계산
    if assessment_results:
        scores = [result["readiness_score"] for result in assessment_results.values()]
        overall_score = round(sum(scores) / len(scores), 1)
        overall_status = get_readiness_status(overall_score, lang)
    else:
        overall_score = 0
        overall_status = "평가 실패" if lang == "ko" else "Assessment Failed"
    
    return {
        "standards": assessment_results,
        "overall_score": overall_score,
        "overall_status": overall_status,
        "_industry": industry or "other",
        "_assessment_method": "enhanced_chatgpt",
        "_focus_standards": focus_standards
    }

def assess_iso_standard_with_chatgpt(company_data: Dict[str, Any], standard: str, iso_spec: Dict[str, Any], 
                                   chatgpt_analyzer: object, lang: str, industry: Optional[str]) -> Dict[str, Any]:
    """ChatGPT를 활용한 ISO 표준별 상세 평가"""
    
    company_name = company_data.get("entity", {}).get("name", "Unknown")
    news_summary = "\n".join([n.get("title", "") + ": " + n.get("excerpt", "")[:200] 
                             for n in company_data.get("news", [])[:5]])
    filings_summary = "\n".join([f.get("title", "") + " (" + f.get("date", "") + ")"
                               for f in company_data.get("filings", [])[:3]])
    
    prompt = f"""
    당신은 ISO {standard} 인증 전문 심사원입니다. 다음 회사의 ISO {standard} ({iso_spec["name"]}) 준비도를 평가해주세요.

    회사명: {company_name}
    산업분류: {industry or "미분류"}
    
    수집된 실제 데이터:
    === 최근 뉴스 ===
    {news_summary}
    
    === 공시정보 ===
    {filings_summary}
    
    === 평가 기준 ===
    다음 각 조항에 대해 0-100점으로 평가하고, 구체적인 갭(부족사항)을 식별해주세요:
    
    {chr(10).join([f"{clause_id}. {clause_data['name']} (가중치: {clause_data['weight']*100}%)" + 
                   chr(10) + "  - " + chr(10).join(clause_data['requirements'])
                   for clause_id, clause_data in iso_spec["clauses"].items()])}
    
    결과를 다음 JSON 형식으로 출력해주세요:
    {{
        {", ".join([f'"{clause_id}": <점수>'for clause_id in iso_spec["clauses"].keys()])},
        {", ".join([f'"{clause_id}_gaps": ["갭1", "갭2", ...]'for clause_id in iso_spec["clauses"].keys()])}
    }}
    
    점수 기준:
    - 90-100: 매우 우수 (거의 완벽한 준비상태)
    - 70-89: 우수 (일부 개선사항 있음)  
    - 50-69: 보통 (상당한 개선 필요)
    - 30-49: 미흡 (많은 개선 필요)
    - 0-29: 매우 미흡 (전면 재검토 필요)
    """
    
    try:
        response = chatgpt_analyzer.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON 추출 및 파싱
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.rfind("```")
            if json_start < json_end:
                result_text = result_text[json_start:json_end].strip()
        elif "{" in result_text and "}" in result_text:
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            result_text = result_text[json_start:json_end]
            
        import json
        return json.loads(result_text)
        
    except Exception as e:
        print(f"ChatGPT ISO 평가 중 오류: {e}")
        # 폴백: 기본 점수 반환
        return {clause_id: 50 for clause_id in iso_spec["clauses"].keys()}

def get_industry_bonus(industry: Optional[str], standard: str) -> float:
    """산업별 보너스 점수"""
    industry_bonus_map = {
        "manufacturing": {"9001": 8, "45001": 5, "14001": 3},
        "construction": {"45001": 10, "14001": 7, "9001": 2},
        "energy": {"14001": 10, "45001": 5, "9001": 2},
        "technology": {"9001": 7, "14001": 3, "45001": 2},
        "healthcare": {"9001": 6, "45001": 8, "14001": 2},
        "finance": {"9001": 5, "14001": 2, "45001": 1},
        "retail": {"9001": 6, "14001": 4, "45001": 3},
        "automotive": {"9001": 9, "45001": 6, "14001": 4},
    }
    return industry_bonus_map.get(industry or "other", {}).get(standard, 0)

def get_readiness_status(score: float, lang: str) -> str:
    """점수에 따른 준비도 상태 반환"""
    if score >= 85:
        return "우수한 준비상태" if lang == "ko" else "Excellent Readiness"
    elif score >= 70:
        return "준비됨" if lang == "ko" else "Ready"
    elif score >= 50:
        return "개선 필요" if lang == "ko" else "Needs Improvement"
    elif score >= 30:
        return "중요 개선 필요" if lang == "ko" else "Critical Improvement Needed"
    else:
        return "전면 재검토 필요" if lang == "ko" else "Complete Overhaul Required"

def iso_readiness_assessment_legacy(keyword_hits_map: Dict[str, int], lang: str = "ko", industry: Optional[str] = None) -> Dict[str, Any]:
    """기존 방식 (ChatGPT 사용 불가시 폴백)"""
    # 기존 하드코딩 로직 유지 (하위 호환성)
    iso_groups = {
        "ko": {
            "9001": ["품질", "고객", "제품", "QC", "QA"],
            "14001": ["환경", "폐기물", "에너지", "탄소", "자원"],
            "45001": ["안전", "재해", "근로", "건강", "노동"],
        },
        "en": {
            "9001": ["quality", "customer", "product", "QC", "QA"],
            "14001": ["environmental", "waste", "energy", "carbon", "resource"],
            "45001": ["safety", "accident", "work", "health", "labor"],
        },
    }
    groups = iso_groups.get(lang, iso_groups["ko"])

    standards: Dict[str, Any] = {}
    for standard, keywords in groups.items():
        relevant_hits = 0
        for pattern, count in (keyword_hits_map or {}).items():
            try:
                if any(kw.lower() in pattern.lower() for kw in keywords):
                    relevant_hits += int(count or 0)
            except Exception:
                continue
        if relevant_hits == 0:
            readiness_score = 75  # 하드코딩 점수 약간 하향 조정
        elif relevant_hits <= 2:
            readiness_score = 60
        elif relevant_hits <= 5:
            readiness_score = 45
        else:
            readiness_score = 30
        
        status = get_readiness_status(readiness_score, lang)
        standards[standard] = {
            "readiness_score": readiness_score,
            "relevant_hits": relevant_hits,
            "status": status,
            "assessment_method": "Legacy Keyword-based"
        }

    scores = [v["readiness_score"] for v in standards.values()] or [0]
    overall_score = round(sum(scores) / len(scores), 1)
    overall_status = get_readiness_status(overall_score, lang)

    return {
        "standards": standards,
        "overall_score": overall_score,
        "overall_status": overall_status,
        "_industry": industry or "other",
        "_assessment_method": "legacy"
    }

# 하위 호환성을 위한 별칭
iso_readiness_assessment = iso_readiness_assessment_legacy

def recommend_iso_standard(iso_assessment: Dict[str, Any], keyword_hits_map: Dict[str, int], lang: str = "ko", industry: Optional[str] = None) -> Dict[str, Any]:
    """ISO 인증 권고안 도출.
    - 기본: 준비도 점수가 가장 높은 표준을 권고
    - 단, 특정 영역(환경/안전/품질) 이슈가 두드러지면 해당 표준을 우선 권고
    """
    if not iso_assessment or "standards" not in iso_assessment:
        return {}

    def localized(txt_ko: str, txt_en: str) -> str:
        return txt_ko if lang == "ko" else txt_en

    standards = iso_assessment.get("standards", {})
    # 우선순위: 환경(14001) / 안전(45001) / 품질(9001) 이슈 강도
    env_hits = 0; saf_hits = 0; qua_hits = 0
    for pattern, count in (keyword_hits_map or {}).items():
        p = (pattern or "").lower(); c = int(count or 0)
        if any(k in p for k in ["환경", "폐기물", "에너지", "탄소", "자원", "environmental", "waste", "energy", "carbon", "resource"]):
            env_hits += c
        if any(k in p for k in ["안전", "재해", "근로", "건강", "노동", "safety", "accident", "work", "health", "labor"]):
            saf_hits += c
        if any(k in p for k in ["품질", "고객", "제품", "qc", "qa", "quality", "customer", "product"]):
            qua_hits += c

    priority_standard = None
    if max(env_hits, saf_hits, qua_hits) > 0:
        if env_hits >= saf_hits and env_hits >= qua_hits:
            priority_standard = "14001"
        elif saf_hits >= env_hits and saf_hits >= qua_hits:
            priority_standard = "45001"
        else:
            priority_standard = "9001"

    # 산업별 우선 순위 보정
    industry_priority: Dict[str, List[str]] = {
        "manufacturing": ["9001", "45001", "14001"],
        "construction": ["45001", "14001", "9001"],
        "energy": ["14001", "45001", "9001"],
        "technology": ["9001", "14001", "45001"],
        "healthcare": ["45001", "9001", "14001"],
        "finance": ["9001", "14001", "45001"],
        "retail": ["9001", "14001", "45001"],
        "automotive": ["9001", "45001", "14001"],
    }
    pref_order = industry_priority.get(industry or iso_assessment.get("_industry") or "other", ["9001", "14001", "45001"])

    # 표준별 종합 랭킹 점수: 준비도(0~100) + 이슈보너스(10) + 산업보너스(5/3/1)
    def rank_score(std: str) -> float:
        base = standards.get(std, {}).get("readiness_score", 0)
        issue_bonus = 10 if std == priority_standard else 0
        try:
            order_bonus = {pref_order[0]: 5, pref_order[1]: 3, pref_order[2]: 1}.get(std, 0)
        except Exception:
            order_bonus = 0
        return base + issue_bonus + order_bonus

    ranked = sorted(["9001", "14001", "45001"], key=lambda s: rank_score(s), reverse=True)
    recommended = ranked[0]
    secondary_std = ranked[1] if len(ranked) > 1 else None

    std_meta = standards.get(recommended, {})
    readiness = std_meta.get("readiness_score", 0)
    status = std_meta.get("status", "")

    if recommended == "14001":
        rationale = localized(
            "환경 이슈의 노출도가 상대적으로 높거나 ESG 요구 대응이 필요한 상황입니다. ISO 14001(환경경영) 인증을 통해 체계적 환경관리와 규제 대응을 강화하는 것이 적절합니다.",
            "Environmental exposures or ESG pressures indicate ISO 14001 will provide the most immediate value."
        )
        next_steps = [
            localized("환경 측면 식별/평가(Aspects & Impacts) 체계화", "Formalize environmental aspects & impacts assessment"),
            localized("법규 준수 평가 및 개선 조치 매트릭스 구축", "Regulatory compliance assessment and corrective matrix"),
            localized("환경목표·지표(KPI) 수립 및 모니터링 루프 설계", "Set environmental KPIs and monitoring loop"),
        ]
    elif recommended == "45001":
        rationale = localized(
            "안전·보건 리스크가 상대적으로 강조됩니다. ISO 45001(안전보건) 인증으로 재해예방, 작업안전 절차 및 교육체계를 선진화하십시오.",
            "Occupational H&S risks are prominent. ISO 45001 will strengthen prevention, controls and training."
        )
        next_steps = [
            localized("위험성 평가(JSA/JHA) 갱신 및 우선순위 위험 저감 계획", "Update risk assessments and high-priority mitigations"),
            localized("안전 리더십·근로자 참여 메커니즘 정착", "Institutionalize safety leadership and worker participation"),
            localized("비상대응 및 성과측정 체계 점검", "Review emergency response and performance measurement"),
        ]
    else:
        rationale = localized(
            "품질/고객/프로세스 관점에서 표준화의 효과가 큽니다. ISO 9001(품질경영)으로 프로세스 일관성과 고객만족을 제고하십시오.",
            "Quality/customer/process signals suggest ISO 9001 to drive consistency and customer satisfaction."
        )
        next_steps = [
            localized("핵심 프로세스 맵 및 절차서 표준화", "Standardize core process maps and procedures"),
            localized("고객 불만·수정/예방조치(CAPA) 체계 최적화", "Optimize complaints and CAPA system"),
            localized("내부심사·경영검토 PDCA 주기 정착", "Institutionalize PDCA through internal audits and management review"),
        ]

    # 2차 권고 구성
    sec_rationale = ""
    sec_steps: List[str] = []
    if secondary_std == "14001":
        sec_rationale = localized("중장기적으로 환경 리스크 대응 역량을 강화하면 ESG 요구 대응과 규제 리스크를 줄일 수 있습니다.", "Secondary: ISO 14001 strengthens ESG/regulatory readiness in the mid-term.")
        sec_steps = [
            localized("환경 법규 레지스터 최신화", "Update environmental legal register"),
            localized("모니터링·측정 장비 교정/검증 체계 정비", "Calibrate/verify monitoring equipment"),
            localized("폐기물/에너지/탄소 데이터 계량화", "Quantify waste/energy/carbon data"),
        ]
    elif secondary_std == "45001":
        sec_rationale = localized("작업장 안전문화 고도화를 통해 재해 발생 가능성을 낮출 수 있습니다.", "Secondary: ISO 45001 reduces incident likelihood via safety culture.")
        sec_steps = [
            localized("행동기반 안전(BBS) 도입 검토", "Consider behavior-based safety (BBS)"),
            localized("중대시민재해법/중대재해법 대응 점검", "Check alignment with local OHS regulations"),
            localized("비상대응 훈련 시나리오 정례화", "Institutionalize emergency drill scenarios"),
        ]
    elif secondary_std == "9001":
        sec_rationale = localized("품질경영 체계를 선진화하면 납기·불량·고객만족 지표가 개선됩니다.", "Secondary: ISO 9001 improves delivery, defects and customer satisfaction.")
        sec_steps = [
            localized("공정능력지수(Cpk) 기반 공정관리 확대", "Expand process control via capability indices (Cpk)"),
            localized("공급업체 평가 및 개발 프로그램 강화", "Strengthen supplier evaluation and development"),
            localized("데이터 기반 CAPA 리포팅 표준화", "Standardize data-driven CAPA reporting"),
        ]

    rec: Dict[str, Any] = {
        "standard": recommended,
        "readiness_score": readiness,
        "status": status,
        "rationale": (f"[{industry}] " if industry else "") + rationale,
        "next_steps": next_steps,
    }
    if secondary_std:
        rec["secondary"] = {
            "standard": secondary_std,
            "readiness_score": standards.get(secondary_std, {}).get("readiness_score", 0),
            "status": standards.get(secondary_std, {}).get("status", ""),
            "rationale": (f"[{industry}] " if industry else "") + sec_rationale,
            "next_steps": sec_steps,
        }
    return rec

def recommend_focused_iso_standard_enhanced(company_data: Dict[str, Any], iso_assessment: Dict[str, Any], 
                                         focus_standards: List[str], chatgpt_analyzer: Optional[object] = None,
                                         lang: str = "ko", industry: Optional[str] = None) -> Dict[str, Any]:
    """✅ 개선된 맞춤형 갭분석 - ChatGPT 기반 실제 회사별 분석"""
    
    if not iso_assessment or "standards" not in iso_assessment or not focus_standards:
        return {}

    standards = iso_assessment.get("standards", {})
    company_name = company_data.get("entity", {}).get("name", "Unknown")
    
    # ChatGPT 기반 맞춤형 갭분석
    if CHATGPT_AVAILABLE and chatgpt_analyzer:
        try:
            return generate_custom_gap_analysis_with_chatgpt(
                company_data, iso_assessment, focus_standards, chatgpt_analyzer, lang, industry
            )
        except Exception as e:
            print(f"ChatGPT 갭분석 실패: {e}, 폴백 분석 사용")
            # 폴백: 기존 템플릿 방식
            return recommend_focused_iso_standard_legacy(
                iso_assessment, {}, focus_standards, lang, industry
            )
    
    # ChatGPT 사용 불가시 기존 방식
    return recommend_focused_iso_standard_legacy(
        iso_assessment, {}, focus_standards, lang, industry
    )

def generate_custom_gap_analysis_with_chatgpt(company_data: Dict[str, Any], iso_assessment: Dict[str, Any],
                                            focus_standards: List[str], chatgpt_analyzer: object,
                                            lang: str, industry: Optional[str]) -> Dict[str, Any]:
    """ChatGPT 기반 실제 회사 맞춤형 갭분석"""
    
    company_name = company_data.get("entity", {}).get("name", "Unknown")
    standards = iso_assessment.get("standards", {})
    
    # 선택된 표준들의 상세 정보 수집
    focus_details = []
    for std in focus_standards:
        if std in standards:
            std_data = standards[std]
            focus_details.append({
                "standard": f"ISO {std}",
                "name": ISO_REQUIREMENTS.get(std, {}).get("name", f"ISO {std}"),
                "score": std_data.get("readiness_score", 0),
                "status": std_data.get("status", ""),
                "clause_details": std_data.get("clause_details", {}),
                "gaps": []
            })
            
            # 조항별 갭 수집
            for clause_id, clause_data in std_data.get("clause_details", {}).items():
                if clause_data.get("score", 100) < 70:  # 70점 미만 갭
                    focus_details[-1]["gaps"].extend(clause_data.get("gaps", []))
    
    # 뉴스 요약
    news_summary = "\n".join([f"- {n.get('title', '')}: {n.get('excerpt', '')[:150]}" 
                             for n in company_data.get("news", [])[:3]])
    
    # 공시 요약  
    filings_summary = "\n".join([f"- {f.get('title', '')} ({f.get('date', '')})"
                                for f in company_data.get("filings", [])[:2]])
    
    prompt = f"""
    당신은 ISO 인증 전문 컨설턴트입니다. 다음 회사의 실제 상황에 기반한 맞춤형 갭분석을 수행해주세요.
    
    === 회사 기본 정보 ===
    회사명: {company_name}
    산업분류: {industry or "미분류"}
    선택 표준: {', '.join([f'ISO {std}' for std in focus_standards])}
    
    === 실제 수집된 데이터 ===
    최근 뉴스:
    {news_summary}
    
    공시 정보:
    {filings_summary}
    
    === 현재 평가 결과 ===
    {chr(10).join([f"ISO {detail['standard'][-4:]}: {detail['score']}/100점 ({detail['status']})" for detail in focus_details])}
    
    === 식별된 주요 갭 ===
    {chr(10).join([f"ISO {detail['standard'][-4:]}: " + ', '.join(detail['gaps'][:3]) for detail in focus_details if detail['gaps']])}
    
    위 실제 데이터를 바탕으로 이 회사만의 구체적이고 실행 가능한 갭분석을 수행해주세요:
    
    1. 이 회사의 현재 상황과 업종 특성을 고려한 준비도 종합 평가
    2. 선택된 표준별 핵심 갭과 원인 분석  
    3. 회사 규모와 역량을 고려한 단계별 개선 방안 (최대 5개)
    4. 실제적인 구현 기간과 예상 비용 범위
    5. 우선순위가 높은 개선 영역 (최대 3개)
    
    결과를 다음 JSON 형식으로 출력해주세요:
    {{
        "type": "custom_gap_analysis",
        "company_specific_assessment": "이 회사의 특수한 상황과 강점/약점",
        "focus_standards": {focus_standards},
        "primary_standard": "가장 우선적으로 추진해야 할 표준",
        "key_gaps": ["핵심 갭1", "핵심 갭2", "핵심 갭3"],
        "customized_recommendations": [
            "구체적 개선방안1", "구체적 개선방안2", "구체적 개선방안3", "구체적 개선방안4", "구체적 개선방안5"
        ],
        "implementation_roadmap": {{
            "phase1": "1-2개월: 즉시 착수 항목",
            "phase2": "3-6개월: 시스템 구축",  
            "phase3": "6-12개월: 운영 정착"
        }},
        "estimated_cost_range": "예상 소요 비용 범위",
        "priority_areas": ["우선순위1", "우선순위2", "우선순위3"],
        "success_factors": ["성공 요인1", "성공 요인2", "성공 요인3"]
    }}
    """
    
    try:
        response = chatgpt_analyzer.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.4
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON 추출
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.rfind("```")
            if json_start < json_end:
                result_text = result_text[json_start:json_end].strip()
        elif "{" in result_text and "}" in result_text:
            json_start = result_text.find("{")
            json_end = result_text.rfind("}") + 1
            result_text = result_text[json_start:json_end]
        
        import json
        gap_analysis = json.loads(result_text)
        
        # 필수 필드 보완
        gap_analysis.update({
            "overall_readiness": iso_assessment.get("overall_score", 0),
            "assessment_method": "ChatGPT Custom Analysis",
            "company_name": company_name,
            "analysis_date": dt.datetime.now().strftime("%Y-%m-%d")
        })
        
        return gap_analysis
        
    except Exception as e:
        print(f"ChatGPT 맞춤형 갭분석 실패: {e}")
        # 폴백
        return {
            "type": "custom_gap_analysis_failed",
            "error": str(e),
            "focus_standards": focus_standards,
            "fallback_used": True
        }

def recommend_focused_iso_standard_legacy(iso_assessment: Dict[str, Any], keyword_hits_map: Dict[str, int], 
                                        focus_standards: List[str], lang: str = "ko", 
                                        industry: Optional[str] = None) -> Dict[str, Any]:
    """기존 템플릿 방식 (폴백용)"""
    if not iso_assessment or "standards" not in iso_assessment or not focus_standards:
        return {}

    def localized(txt_ko: str, txt_en: str) -> str:
        return txt_ko if lang == "ko" else txt_en

    standards = iso_assessment.get("standards", {})
    
    # 포커스 표준 중 가장 높은 점수의 표준을 주요 권고로 설정
    best_standard = None
    best_score = -1
    
    for std in focus_standards:
        if std in standards:
            score = standards[std].get("readiness_score", 0)
            if score > best_score:
                best_score = score
                best_standard = std
    
    if not best_standard:
        return {}
    
    # 기본 템플릿 적용
    template_map = {
        "14001": {
            "rationale": localized(
                f"ISO 14001(환경경영) 갭분석 결과 현재 준비도는 {best_score}/100점입니다. 환경 리스크 관리 체계 구축과 법규 준수 강화가 필요합니다.",
                f"ISO 14001 gap analysis shows {best_score}/100 readiness. Environmental risk management system and regulatory compliance need strengthening."
            ),
            "next_steps": [
                localized("환경 법규 확인 및 준수 체계 구축", "Establish environmental regulation compliance system"),
                localized("환경 영향 평가 프로세스 개발", "Develop environmental impact assessment process"),
                localized("환경 목표 및 모니터링 지표 설정", "Set environmental objectives and monitoring indicators"),
                localized("직원 환경 교육 프로그램 실시", "Implement employee environmental training program"),
                localized("폐기물 관리 및 에너지 효율성 개선", "Improve waste management and energy efficiency")
            ]
        },
        "45001": {
            "rationale": localized(
                f"ISO 45001(안전보건) 갭분석 결과 현재 준비도는 {best_score}/100점입니다. 작업장 안전 문화 강화와 위험성 평가 체계 구축이 필요합니다.",
                f"ISO 45001 gap analysis shows {best_score}/100 readiness. Workplace safety culture and hazard assessment system need enhancement."
            ),
            "next_steps": [
                localized("위험성 평가 및 관리 체계 구축", "Establish hazard assessment and management system"),
                localized("안전보건 정책 및 절차 수립", "Develop safety and health policies and procedures"),
                localized("근로자 참여 및 협의 체계 강화", "Strengthen worker participation and consultation system"),
                localized("사고 예방 및 응급 대응 계획 수립", "Develop accident prevention and emergency response plans"),
                localized("안전보건 교육 및 역량 강화", "Enhance safety and health training and competency")
            ]
        }
    }
    
    # 기본값 (9001)
    template = template_map.get(best_standard, {
        "rationale": localized(
            f"ISO 9001(품질경영) 갭분석 결과 현재 준비도는 {best_score}/100점입니다. 품질 관리 체계 강화와 고객 만족도 향상이 필요합니다.",
            f"ISO 9001 gap analysis shows {best_score}/100 readiness. Quality management system and customer satisfaction need improvement."
        ),
        "next_steps": [
            localized("품질 방침 및 목표 수립", "Establish quality policy and objectives"),
            localized("프로세스 접근법 기반 품질시스템 구축", "Build quality system based on process approach"),
            localized("고객 요구사항 관리 체계 강화", "Strengthen customer requirements management system"),
            localized("내부 심사 및 관리 검토 체계 구축", "Establish internal audit and management review system"),
            localized("지속적 개선 문화 정착", "Establish continuous improvement culture")
        ]
    })
    
    return {
        "type": "focused_gap_analysis_legacy",
        "focus_standards": focus_standards,
        "primary_standard": best_standard,
        "primary_score": best_score,
        "rationale": template["rationale"],
        "next_steps": template["next_steps"][:5],
        "implementation_timeline": localized("3-6개월 집중 준비 권장", "3-6 months intensive preparation recommended"),
        "assessment_method": "Template-based Legacy"
    }

# 하위 호환성을 위한 별칭
recommend_focused_iso_standard = recommend_focused_iso_standard_legacy

def analyze_company_with_chatgpt(data: Dict, company_name: str) -> Dict:
    """ChatGPT API를 활용한 지능형 종합 분석"""
    
    if not CHATGPT_AVAILABLE:
        return {
            "error": "ChatGPT API를 사용할 수 없습니다.",
            "fallback": True
        }
    
    try:
        # ChatGPT 분석기 인스턴스 생성
        analyzer = ChatGPTEnhancedAnalyzer(CHATGPT_API_KEY)
        
        # 데이터 추출
        news_data = data.get("news", [])
        social_data = data.get("social_media", [])
        filings_data = data.get("filings", [])
        
        # 맥락적 리스크 분석
        contextual_analysis = analyzer.analyze_risk_context(
            company_name, news_data, social_data, filings_data, industry=None
        )
        
        # 현재 데이터로 리스크 시나리오 생성 (RAG 근거 포함)
        current_risk_data = {
            "risk_score": data.get("risk", {}).get("risk_score_0to1", "N/A"),
            "risk_factors": list(data.get("risk", {}).get("keyword_hits", {}).keys())[:5]
        }
        def _build_sources(items: List[Dict[str, Any]], prefix: str) -> List[Dict[str, str]]:
            srcs: List[Dict[str, str]] = []
            for idx, it in enumerate(items[:10], start=1):
                srcs.append({
                    "id": f"{prefix}{idx}",
                    "title": it.get("title") or it.get("type") or prefix,
                    "date": (it.get("published") or it.get("date") or "")[:10],
                    "url": it.get("url") or it.get("link") or "#",
                })
            return srcs
        sources = _build_sources(news_data, "N") + _build_sources(filings_data, "F")
        risk_scenarios = analyzer.generate_risk_scenarios(company_name, current_risk_data, industry=None, sources=sources)
        
        # 맞춤형 보고서 생성 (경영진용)
        executive_report = analyzer.generate_personalized_report(
            company_name, "경영진", data
        )
        
        # 맞춤형 보고서 생성 (투자자용)
        investor_report = analyzer.generate_personalized_report(
            company_name, "투자자", data
        )
        
        return {
            "contextual_analysis": {
                "hidden_risks": contextual_analysis.hidden_risks,
                "market_context": contextual_analysis.market_context,
                "competitive_analysis": contextual_analysis.competitive_analysis,
                "regulatory_implications": contextual_analysis.regulatory_implications,
                "investor_sentiment": contextual_analysis.investor_sentiment,
                "recommendations": contextual_analysis.recommendations
            },
            "risk_scenarios": [
                {
                    "scenario_id": scenario.scenario_id,
                    "title": scenario.title,
                    "description": scenario.description,
                    "probability": scenario.probability,
                    "impact": scenario.impact,
                    "risk_level": scenario.risk_level,
                    "triggers": scenario.triggers,
                    "mitigation_strategies": scenario.mitigation_strategies,
                    "timeline": scenario.timeline,
                    "confidence": scenario.confidence
                }
                for scenario in risk_scenarios
            ],
            "personalized_reports": {
                "executive": executive_report,
                "investor": investor_report
            },
            "analysis_method": "ChatGPT GPT-4o-mini + 기존 분석 시스템",
            "ai_enhanced": True
        }
        
    except Exception as e:
        return {
            "error": f"ChatGPT 분석 중 오류 발생: {str(e)}",
            "fallback": True
        }

# ---------------------------
# Chart → base64
# ---------------------------
def risk_chart_base64(finbert: Dict[str, float], keyword_hits: Dict[str, int] = None) -> str:
    # 폰트 설정 - 한글 지원 폰트 우선, 없으면 기본 폰트
    try:
        plt.rcParams['font.family'] = ['Malgun Gothic', 'NanumGothic', 'DejaVu Sans', 'Arial']
    except:
        plt.rcParams['font.family'] = 'DejaVu Sans'
    
    # 서브플롯 생성 (2x2 그리드)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8), dpi=150)
    
    # 1. FinBERT 감성분석 결과 (왼쪽 상단)
    labels = ["Negative", "Neutral", "Positive"]
    vals = [finbert.get("neg", 0), finbert.get("neu", 0), finbert.get("pos", 0)]
    colors = ['#ef4444', '#6b7280', '#10b981']
    
    bars1 = ax1.bar(labels, vals, color=colors, alpha=0.8)
    ax1.set_ylim(0, 1)
    ax1.set_title("FinBERT Sentiment Analysis", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Probability (0~1)")
    
    # 값 표시
    for bar, val in zip(bars1, vals):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. 감성 분포 파이 차트 (오른쪽 상단)
    if sum(vals) > 0:
        ax2.pie(vals, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title("Sentiment Distribution", fontsize=14, fontweight='bold')
    
    # 3. 키워드 히트 차트 (왼쪽 하단)
    if keyword_hits and any(keyword_hits.values()):
        keywords = list(keyword_hits.keys())
        counts = list(keyword_hits.values())
        
        # 키워드 이름을 더 읽기 쉽게 변환
        keyword_labels = []
        for kw in keywords:
            if '|' in kw:
                # 정규표현식에서 첫 번째 패턴만 사용
                clean_kw = kw.split('|')[0]
            else:
                clean_kw = kw
            keyword_labels.append(clean_kw[:15])  # 15자로 제한
        
        bars3 = ax3.barh(keyword_labels, counts, color='#3b82f6', alpha=0.8)
        ax3.set_title("Risk Keyword Hits", fontsize=14, fontweight='bold')
        ax3.set_xlabel("Count")
        
        # 값 표시
        for bar, count in zip(bars3, counts):
            width = bar.get_width()
            ax3.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    str(count), ha='left', va='center', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, "No Risk Keywords\nFound", ha='center', va='center', 
                transform=ax3.transAxes, fontsize=12, color='gray')
        ax3.set_title("Risk Keyword Hits", fontsize=14, fontweight='bold')
    
    # 4. 종합 리스크 지표 (오른쪽 하단)
    risk_score = 0.6 * finbert.get("neg", 0) + 0.4 * (min(1.0, 0.2 * (1 + (sum(keyword_hits.values()) if keyword_hits else 0) ** 0.5)))
    
    # 리스크 레벨 결정
    if risk_score < 0.3:
        risk_level = "Low"
        risk_color = "#10b981"
    elif risk_score < 0.6:
        risk_level = "Medium"
        risk_color = "#f59e0b"
    else:
        risk_level = "High"
        risk_color = "#ef4444"
    
    # 게이지 차트 스타일
    ax4.barh(['Risk'], [risk_score], color=risk_color, alpha=0.8, height=0.3)
    ax4.set_xlim(0, 1)
    ax4.set_title(f"Overall Risk Score", fontsize=14, fontweight='bold')
    ax4.set_xlabel("Risk Score (0~1)")
    
    # 리스크 점수와 레벨 표시
    ax4.text(risk_score/2, 0, f'{risk_score:.3f}\n({risk_level})', 
             ha='center', va='center', fontweight='bold', fontsize=12)
    
    plt.tight_layout()
    
    # 차트를 base64로 인코딩
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# ---------------------------
# HTML Template
# ---------------------------
HTML_TEMPLATE = Template(r"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>{{ title }}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", Arial, sans-serif; margin: 28px; }
  h1 { font-size: 22px; margin: 0 0 6px 0; }
  h2 { font-size: 18px; margin: 22px 0 8px 0; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
  .meta { color:#555; font-size: 12px; margin-bottom: 18px; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { border: 1px solid #e5e7eb; padding: 6px 8px; vertical-align: top; }
  th { background:#f8fafc; text-align:left; }
  .small { font-size: 11px; color:#555; }
  .chip { display:inline-block; padding:2px 6px; border-radius: 10px; background:#eef2ff; margin-right:6px; font-size: 11px;}
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .card { border:1px solid #eee; border-radius:12px; padding:12px; }
  .muted { color:#6b7280; }
     img.chart { width: 100%; max-width: 800px; height: auto; }
  .nowrap { white-space: nowrap; }
</style>
</head>
<body>
  <h1>회사 리스크 & 인텔리전스 리포트</h1>
  <div class="meta">
    생성시각(UTC): {{ timestamp }} | 입력: {{ input.company_name or "-" }} / {{ input.url or "-" }} / lang={{ input.lang }}
  </div>

  <div class="grid">
    <div class="card">
      <strong>엔티티</strong><br/>
      이름: {{ entity.name or "-" }}<br/>
      도메인: {{ entity.domain or "-" }}
    </div>
         <div class="card">
       <strong>리스크 요약</strong><br/>
       FinBERT 평균 — NEG: {{ risk.finbert.neg | round(3) }}, NEU: {{ risk.finbert.neu | round(3) }}, POS: {{ risk.finbert.pos | round(3) }}<br/>
       키워드 총 히트: {{ risk.keyword_hits_total }}<br/>
       <strong>종합 리스크 스코어(0~1): {{ risk.risk_score_0to1 }}</strong><br/><br/>
       
       <div style="background: #f8fafc; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
         <strong>📊 분석 결과 해석:</strong><br/>
         <strong>• FinBERT 감성분석:</strong> 금융 전문 AI 모델이 뉴스와 텍스트를 분석한 결과입니다.<br/>
         &nbsp;&nbsp;- <span style="color: #ef4444;">부정(NEG): {{ risk.finbert.neg | round(3) }}</span> - 리스크 지표로 사용됩니다<br/>
         &nbsp;&nbsp;- <span style="color: #6b7280;">중립(NEU): {{ risk.finbert.neu | round(3) }}</span> - 일반적인 업무 관련 뉴스<br/>
         &nbsp;&nbsp;- <span style="color: #10b981;">긍정(POS): {{ risk.finbert.pos | round(3) }}</span> - 긍정적인 소식<br/>
         <strong>• 키워드 히트:</strong> 리스크 관련 키워드가 {{ risk.keyword_hits_total }}건 발견되었습니다.<br/>
         <strong>• 종합 리스크:</strong> {{ risk.risk_score_0to1 }}로 {% if risk.risk_score_0to1 < 0.3 %}낮은{% elif risk.risk_score_0to1 < 0.6 %}보통{% else %}높은{% endif %} 위험도입니다.
       </div>
       
       {% if chart_b64 %}
       <img class="chart" src="data:image/png;base64,{{ chart_b64 }}" alt="risk chart"/>
       <div class="chart-explanation" style="margin-top: 12px; font-size: 11px; color: #666;">
         <strong>📊 차트 설명:</strong><br/>
         • <strong>왼쪽 상단:</strong> FinBERT AI 모델이 분석한 텍스트의 감성 분포 (부정/중립/긍정 확률)<br/>
         • <strong>오른쪽 상단:</strong> 감성 분포를 원형 차트로 시각화<br/>
         • <strong>왼쪽 하단:</strong> 리스크 관련 키워드가 뉴스/텍스트에서 발견된 횟수<br/>
         • <strong>오른쪽 하단:</strong> 종합 리스크 점수와 위험도 레벨 (낮음/보통/높음)
       </div>
       {% endif %}
     </div>
  </div>

   <h2>ISO 인증 준비도 평가 및 권고</h2>
   <div class="grid">
     <div class="card">
       <strong>ISO 9001 (품질경영)</strong><br/>
       준비도 점수: <strong>{{ iso_assessment.standards['9001'].readiness_score if iso_assessment and iso_assessment.standards and '9001' in iso_assessment.standards else '-' }}/100</strong><br/>
       상태: <span class="chip">{{ iso_assessment.standards['9001'].status if iso_assessment and iso_assessment.standards and '9001' in iso_assessment.standards else '-' }}</span><br/>
       관련 리스크 히트: {{ iso_assessment.standards['9001'].relevant_hits if iso_assessment and iso_assessment.standards and '9001' in iso_assessment.standards else '-' }}
     </div>
     <div class="card">
       <strong>ISO 14001 (환경경영)</strong><br/>
       준비도 점수: <strong>{{ iso_assessment.standards['14001'].readiness_score if iso_assessment and iso_assessment.standards and '14001' in iso_assessment.standards else '-' }}/100</strong><br/>
       상태: <span class="chip">{{ iso_assessment.standards['14001'].status if iso_assessment and iso_assessment.standards and '14001' in iso_assessment.standards else '-' }}</span><br/>
       관련 리스크 히트: {{ iso_assessment.standards['14001'].relevant_hits if iso_assessment and iso_assessment.standards and '14001' in iso_assessment.standards else '-' }}
     </div>
     <div class="card">
       <strong>ISO 45001 (안전보건)</strong><br/>
       준비도 점수: <strong>{{ iso_assessment.standards['45001'].readiness_score if iso_assessment and iso_assessment.standards and '45001' in iso_assessment.standards else '-' }}/100</strong><br/>
       상태: <span class="chip">{{ iso_assessment.standards['45001'].status if iso_assessment and iso_assessment.standards and '45001' in iso_assessment.standards else '-' }}</span><br/>
       관련 리스크 히트: {{ iso_assessment.standards['45001'].relevant_hits if iso_assessment and iso_assessment.standards and '45001' in iso_assessment.standards else '-' }}
     </div>
     <div class="card">
       <strong>전체 준비도</strong><br/>
       평균 점수: <strong>{{ iso_assessment.overall_score if iso_assessment else '-' }}/100</strong><br/>
       전체 상태: <span class="chip">{{ iso_assessment.overall_status if iso_assessment else '-' }}</span><br/>
       인증 권고: <span style="font-weight:bold; color:#1f2937;">{{ iso_recommendation.standard if iso_recommendation else '-' }}</span>
       {% if iso_recommendation and iso_recommendation.secondary %}<br/>
       2차 권고: <span class="chip">{{ iso_recommendation.secondary.standard }}</span>
       {% endif %}
     </div>
   </div>
   {% if iso_recommendation %}
   <div class="card" style="margin-top:12px;">
     <strong>권고 사유:</strong><br/>
     <div class="small">{{ iso_recommendation.rationale }}</div>
     <div class="small" style="margin-top:8px;"><strong>다음 단계(Top 3):</strong>
       <ul>
         {% for step in iso_recommendation.next_steps %}
           <li>{{ step }}</li>
         {% endfor %}
       </ul>
     </div>
     {% if iso_recommendation.secondary %}
     <div class="small" style="margin-top:8px;"><strong>2차 권고 사유:</strong> {{ iso_recommendation.secondary.rationale }}</div>
     <div class="small" style="margin-top:6px;"><strong>2차 다음 단계:</strong>
       <ul>
         {% for step in iso_recommendation.secondary.next_steps %}
           <li>{{ step }}</li>
         {% endfor %}
       </ul>
     </div>
     {% endif %}
   </div>
   {% endif %}

      <h2>공시 (최신)</h2>
   {% if filings %}
   <table>
     <tr><th class="nowrap">날짜</th><th>출처</th><th>유형/제목</th></tr>
     {% for f in filings %}
     <tr>
       <td class="nowrap">{{ f.date or "" }}</td>
       <td>{{ f.source }}</td>
       <td><a href="{{ f.url }}" target="_blank" style="color: #2563eb; text-decoration: none;">{{ f.type or "" }} — {{ f.title or "" }}</a></td>
     </tr>
     {% endfor %}
   </table>
   {% else %}
   <div class="muted small">공시 데이터 없음 (API 키 미설정 / 미상장 / 미지원)</div>
   {% endif %}

     <h2>뉴스 Top</h2>
   {% if news %}
   <table>
     <tr><th class="nowrap">발행</th><th>제목</th><th>요약</th></tr>
     {% for n in news %}
     <tr>
       <td class="nowrap">{{ n.published or "" }}</td>
       <td><a href="{{ n.url }}" target="_blank" style="color: #2563eb; text-decoration: none;">{{ n.title or "" }}</a></td>
       <td class="small">{{ n.excerpt or "" }}</td>
     </tr>
     {% endfor %}
   </table>
   {% else %}
   <div class="muted small">최근 2주간 뉴스 수집 없음</div>
   {% endif %}

           <h2>소셜미디어 (Reddit + Stocktwits)</h2>
    {% if social_media %}
      {% if social_media[0].error %}
        <div class="muted small" style="background: #fef3c7; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b;">
          <strong>소셜미디어 데이터 수집 실패:</strong><br/>
          {{ social_media[0].error }}
        </div>
      {% else %}
        <table>
          <tr><th class="nowrap">시간</th><th>플랫폼</th><th>작성자</th><th>내용</th></tr>
          {% for post in social_media %}
          <tr>
            <td class="nowrap">{{ post.date or "" }}</td>
            <td>{{ post.source }}</td>
            <td>{{ post.user or "" }}</td>
            <td class="small"><a href="{{ post.url }}" target="_blank" style="color: #2563eb; text-decoration: none;">{{ post.content or "" }}</a></td>
          </tr>
          {% endfor %}
        </table>
      {% endif %}
    {% else %}
    <div class="muted small">최근 2주간 소셜미디어 데이터 수집 없음</div>
    {% endif %}

      <h2>트위터 (X) - API 키 필요</h2>
    {% if tweets %}
      {% if tweets[0].error %}
        <div class="muted small" style="background: #fef3c7; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b;">
          <strong>트위터 API 설정 필요:</strong><br/>
          {{ tweets[0].error }}<br/>
          <small>트위터 데이터를 수집하려면 환경변수에 API 키를 설정하세요:<br/>
          TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET</small>
        </div>
      {% else %}
        <table>
          <tr><th class="nowrap">시간</th><th>작성자</th><th>내용</th></tr>
          {% for t in tweets %}
          <tr>
            <td class="nowrap">{{ t.date or "" }}</td>
            <td>@{{ t.user or "" }}</td>
            <td class="small"><a href="{{ t.url }}" target="_blank" style="color: #2563eb; text-decoration: none;">{{ t.content or "" }}</a></td>
          </tr>
          {% endfor %}
        </table>
      {% endif %}
    {% else %}
    <div class="muted small">최근 2주간 트윗 수집 없음</div>
    {% endif %}

     <h2>키워드 히트(리스크 사전)</h2>
   <div>
     {% if risk.keyword_hits_total > 0 %}
       <div style="margin-bottom: 12px;">
         <strong>🔍 발견된 리스크 키워드:</strong>
       </div>
       {% for pat, cnt in risk.keyword_hits.items() %}
         {% if cnt > 0 %}
           <span class="chip" style="background: #fee2e2; color: #dc2626; border: 1px solid #fecaca;">
             {{ pat.split('|')[0] }}: {{ cnt }}
           </span>
         {% endif %}
       {% endfor %}
     {% else %}
       <div style="background: #f0fdf4; padding: 12px; border-radius: 8px; border-left: 4px solid #22c55e;">
         <strong>✅ 리스크 키워드 발견 없음</strong><br/>
         <small>분석된 뉴스와 텍스트에서 리스크 관련 키워드가 발견되지 않았습니다.<br/>
         이는 현재 시점에서 특별한 리스크 이슈가 없음을 의미할 수 있습니다.</small>
       </div>
     {% endif %}
   </div>

</body>
</html>
""")

# ---------------------------
# Build Report (collect + score)
# ---------------------------
def build_report(
    company_name: Optional[str],
    url: Optional[str],
    country_hint: Optional[str],
    lang: str,
    use_serpapi: bool = False,
    serpapi_key: Optional[str] = None,
    sec_ticker: Optional[str] = None,
    sec_cik: Optional[str] = None,
    sec_forms: Optional[str] = None,
    sec_from_date: Optional[str] = None,
    sec_to_date: Optional[str] = None,
    iso_focus: Optional[List[str]] = None,
    output_format: str = "html"
):
    entity = identify_company(company_name, url)
    cname = entity["name"] or entity["domain"] or "Unknown"
    base_id = sanitize_filename(cname + "_" + (entity["domain"] or "")) or "company"

    filings: List[Dict[str, Any]] = []
    if country_hint and country_hint.upper() == "KR" and entity["name"]:
        filings += fetch_dart_filings(entity["name"])
    if entity["name"]:
        forms_list = None
        if sec_forms:
            try:
                forms_list = [s.strip() for s in sec_forms.split(',') if s.strip()]
            except Exception:
                forms_list = None
        filings += fetch_sec_filings_by_name(
            entity["name"],
            ticker=sec_ticker,
            cik=sec_cik,
            form_types=forms_list,
            from_date=sec_from_date,
            to_date=sec_to_date,
        )

    news: List[Dict[str, Any]] = []
    if use_serpapi and serpapi_key:
        news = fetch_news_serpapi_with_fallback(entity["name"] or (entity["domain"] or ""), lang=lang, days=14, limit=8, api_key=serpapi_key, location="South Korea" if (lang or "ko").startswith("ko") else None)
    if not news:
        news = fetch_news(entity["name"] or (entity["domain"] or ""), lang=lang, days=14, limit=8)
    
    # 소셜미디어 데이터 수집 (Reddit + Stocktwits 우선, Twitter는 API 키가 있는 경우)
    social_media = fetch_social_media(entity["name"] or (entity["domain"] or ""), since_days=14, limit=20)
    tweets = fetch_tweets(entity["name"] or (entity["domain"] or ""), since_days=14, limit=10)  # Twitter는 보조로

    texts = [n.get("title","") + " " + n.get("excerpt","") for n in news[:8]] + \
            [post.get("content","") for post in social_media[:20]] + \
            [t.get("content","") for t in tweets[:10]]
    finbert = FinBertScorer().score(texts)
    hits = keyword_hits(texts, RISK_KEYWORDS)
    rscore = simple_risk_score(finbert, hits)

    # 기본 리스크 분석 실행 (ISO 31000 제외)
    baseline_risk_analysis = analyze_company_risks_baseline({
        "news": news,
        "social_media": social_media,
        "tweets": tweets,
        "risk": {
            "finbert": finbert,
            "keyword_hits": hits
        }
    })

    # ✅ 개선된 ISO 9001/14001/45001 준비도 평가 (실제 요구사항 기반)
    inferred_industry = infer_industry(entity, news, filings)
    
    # 회사 데이터 패키지 준비
    company_analysis_data = {
        "entity": entity,
        "news": news,
        "filings": filings,
        "social_media": social_media,
        "tweets": tweets,
        "keyword_hits": hits,
        "industry": inferred_industry
    }
    
    # ChatGPT 분석기 준비 (가능한 경우)
    chatgpt_analyzer = None
    if CHATGPT_AVAILABLE and CHATGPT_API_KEY:
        try:
            chatgpt_analyzer = ChatGPTEnhancedAnalyzer(CHATGPT_API_KEY)
        except Exception as e:
            print(f"ChatGPT 분석기 초기화 실패: {e}")
    
    # 새로운 평가 시스템 적용 (ChatGPT 기반)
    if chatgpt_analyzer:
        print("🤖 ChatGPT 기반 실제 ISO 요구사항 평가 수행 중...")
        iso_assessment = iso_readiness_assessment_enhanced(
            company_analysis_data, 
            chatgpt_analyzer, 
            lang=lang, 
            industry=inferred_industry,
            focus_standards=iso_focus
        )
    else:
        print("⚠️ ChatGPT 사용 불가, 기존 키워드 기반 평가로 폴백")
        iso_assessment = iso_readiness_assessment_legacy(hits, lang=lang, industry=inferred_industry)
    
    # 🆕 맞춤형 갭분석: 선택된 ISO 표준에 집중
    if iso_focus:
        # 선택된 표준만으로 필터링된 assessment 생성
        focused_assessment = {'standards': {}, 'overall_score': 0, 'overall_status': 'pending'}
        total_score = 0
        count = 0
        
        for iso_std in iso_focus:
            if iso_std in iso_assessment.get('standards', {}):
                focused_assessment['standards'][iso_std] = iso_assessment['standards'][iso_std]
                total_score += iso_assessment['standards'][iso_std].get('readiness_score', 0)
                count += 1
        
        if count > 0:
            focused_assessment['overall_score'] = total_score / count
            focused_assessment['overall_status'] = 'analyzed'
            focused_assessment['_focus_standards'] = iso_focus  # 추가 정보
        
        # 포커스된 assessment로 교체
        iso_assessment = focused_assessment
        
        # 🆕 ChatGPT 기반 맞춤형 갭분석 권고 생성
        if chatgpt_analyzer:
            print("🎯 ChatGPT 기반 맞춤형 갭분석 수행 중...")
            iso_recommendation = recommend_focused_iso_standard_enhanced(
                company_analysis_data, iso_assessment, iso_focus, 
                chatgpt_analyzer, lang=lang, industry=inferred_industry
            )
        else:
            print("⚠️ ChatGPT 사용 불가, 기본 템플릿 갭분석 사용")
            iso_recommendation = recommend_focused_iso_standard_legacy(
                iso_assessment, hits, iso_focus, lang=lang, industry=inferred_industry
            )
    else:
        # 기존 방식 유지
        iso_recommendation = recommend_iso_standard(iso_assessment, hits, lang=lang, industry=inferred_industry)

    # ChatGPT API를 활용한 지능형 분석 실행
    chatgpt_analysis = analyze_company_with_chatgpt({
        "news": news,
        "social_media": social_media,
        "tweets": tweets,
        "filings": filings,
        "risk": {
            "finbert": finbert,
            "keyword_hits": hits,
            "risk_score_0to1": rscore
        }
    }, company_name)

    # --- 변화 추적 및 시나리오 기반 보정 ---
    def _scenario_numeric_score(s: Dict[str, Any]) -> int:
        prob_map = {"매우 높음":5, "높음":4, "보통":3, "낮음":2, "매우 낮음":1}
        impact_map = prob_map
        ln = s.get('likelihood_num') or prob_map.get(s.get('probability',''), 0)
        im = s.get('impact_num') or impact_map.get(s.get('impact',''), 0)
        try:
            return int(ln) * int(im)
        except Exception:
            return 0

    current_scenarios: List[Dict[str, Any]] = chatgpt_analysis.get("risk_scenarios", []) if isinstance(chatgpt_analysis, dict) else []
    current_scores: Dict[str, int] = { s.get('title',''): _scenario_numeric_score(s) for s in current_scenarios if s.get('title') }
    current_titles: List[str] = list(current_scores.keys())

    prev_titles: List[str] = []
    prev_scores: Dict[str, int] = {}
    try:
        prev_path = DATA_DIR / f"{base_id}.json"
        if prev_path.exists():
            with open(prev_path, 'r', encoding='utf-8') as f:
                prev_data = json.load(f)
                prev_titles = prev_data.get('current_scenario_titles', []) or prev_data.get('previous_scenario_titles', []) or []
                prev_scores = prev_data.get('current_scenario_scores', {}) or prev_data.get('previous_scenario_scores', {}) or {}
    except Exception:
        pass

    # 시나리오 점수 신호(0~1) 계산: 상위 3개 평균을 25로 정규화
    top_scores = sorted(current_scores.values(), reverse=True)[:3]
    scenario_signal = 0.0
    if top_scores:
        scenario_signal = min(1.0, (sum(top_scores)/max(1, len(top_scores))) / 25.0)
    # 기존 리스크 스코어 보정
    rscore = float(rscore)
    adjusted_risk = round(0.7 * rscore + 0.3 * scenario_signal, 3)

    serpapi_bundle: Dict[str, Any] = {}
    if use_serpapi and serpapi_key:
        alias_queries = build_alias_queries(cname, entity.get("domain"))
        q_alias = alias_queries[0] if alias_queries else cname
        try:
            serpapi_bundle["trends"] = fetch_trends_serpapi(q_alias, serpapi_key, geo="KR" if (lang or "ko").startswith("ko") else "US")
        except Exception:
            serpapi_bundle["trends"] = {"error": "트렌드 데이터 수집 중 오류 발생"}
        try:
            serpapi_bundle["patents"] = fetch_patents_serpapi(f'{q_alias} litigation OR infringement OR lawsuit', serpapi_key, limit=10)
        except Exception:
            serpapi_bundle["patents"] = {"error": "특허 데이터 수집 중 오류 발생"}
        try:
            serpapi_bundle["ai_overview"] = fetch_ai_overview_serpapi(q_alias, lang or "ko", serpapi_key, location="South Korea" if (lang or "ko").startswith("ko") else None)
        except Exception:
            serpapi_bundle["ai_overview"] = {"error": "AI Overview 수집 중 오류 발생"}
        try:
            serpapi_bundle["related_questions"] = fetch_related_questions_serpapi(q_alias, lang or "ko", serpapi_key, location="South Korea" if (lang or "ko").startswith("ko") else None)
        except Exception:
            serpapi_bundle["related_questions"] = {"error": "관련 질문 수집 중 오류 발생"}
        try:
            serpapi_bundle["youtube"] = fetch_youtube_serpapi(q_alias, serpapi_key, lang=lang or "ko", limit=8)
        except Exception:
            serpapi_bundle["youtube"] = {"error": "YouTube 데이터 수집 중 오류 발생"}
        try:
            serpapi_bundle["naver"] = fetch_naver_serpapi(q_alias, serpapi_key, limit=10)
        except Exception:
            serpapi_bundle["naver"] = {"error": "Naver 데이터 수집 중 오류 발생"}

    bundle = {
        "timestamp": now_utc_iso(),
        "input": {"company_name": company_name, "url": url, "country_hint": country_hint, "lang": lang},
        "entity": entity,
        "filings": filings,
        "news": news,
        "social_media": social_media[:50],
        "tweets": tweets[:50],
        # SerpApi는 보고서 표시는 하지 않되, 분석용으로만 보관
        "serpapi": serpapi_bundle,
        "risk": {
            "finbert": finbert,
            "keyword_hits": hits,
            "keyword_hits_total": int(sum(hits.values())),
            "risk_score_0to1": adjusted_risk
        },
        "iso_assessment": iso_assessment,
        "iso_recommendation": iso_recommendation,
        "baseline_risk_analysis": baseline_risk_analysis,
        "chatgpt_enhanced_analysis": chatgpt_analysis,
        "previous_scenario_titles": prev_titles,
        "previous_scenario_scores": prev_scores,
        "current_scenario_titles": current_titles,
        "current_scenario_scores": current_scores,
        "_base_id": base_id
    }
    save_json(bundle, DATA_DIR / f"{base_id}.json")
    return bundle

# ---------------------------
# HTML Render + PDF
# ---------------------------
def render_html(report: Dict[str, Any]) -> str:
    chart_b64 = risk_chart_base64(report["risk"]["finbert"], report["risk"]["keyword_hits"])
    html = HTML_TEMPLATE.render(
        title=f"리포트 - {report['entity'].get('name') or report['entity'].get('domain') or 'Company'}",
        chart_b64=chart_b64, **report
    )
    return html

def generate_iso31000_report(report: Dict[str, Any], outdir: Path) -> Path:
    """(비활성화) ISO 31000 보고서는 제거되었습니다."""
    return None

def generate_chatgpt_enhanced_report(report: Dict[str, Any], outdir: Path) -> Path:
    """ChatGPT API를 활용한 지능형 종합 분석보고서 생성"""
    if not CHATGPT_AVAILABLE:
        print("[WARN] ChatGPT API를 사용할 수 없습니다. 지능형 보고서 생성을 건너뜁니다.")
        return None
    
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        base = report["_base_id"]
        chatgpt_path = outdir / f"{base}_AI_지능형분석보고서_2025.html"
        
        chatgpt_html_content = generate_chatgpt_html_report(report, report["chatgpt_enhanced_analysis"])
        
        with open(chatgpt_path, "w", encoding="utf-8") as f:
            f.write(chatgpt_html_content)
        print(f"[OK] ChatGPT 지능형 분석보고서 생성 완료: {chatgpt_path}")
        return chatgpt_path
    except Exception as e:
        print(f"❌ ChatGPT 지능형 보고서 생성 중 오류 발생: {e}")
        return None

def generate_iso31000_html_report(report: Dict[str, Any], iso31000_data: Dict[str, Any]) -> str:
    """(비활성화) ISO 31000 HTML 생성은 제거되었습니다."""
    return ""
    
    company_name = report['entity'].get('name') or report['entity'].get('domain') or 'Unknown'
    current_date = dt.datetime.now().strftime("%Y년 %m월 %d일")
    
    # ISO 31000 비활성화
    
    # 리스크 레벨에 따른 색상 결정
    risk_colors = {
        "매우 낮음": "#28a745",
        "낮음": "#6f42c1", 
        "보통": "#ffc107",
        "높음": "#fd7e14",
        "매우 높음": "#dc3545"
    }
    risk_color = risk_colors.get(overall_level, "#6c757d")
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} 비즈니스 인텔리전스 리포트 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .iso-badge {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 10px;
            border-left: 5px solid #1e3c72;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .section h2 {{
            color: #1e3c72;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .section h3 {{
            color: #2a5298;
            font-size: 1.4em;
            margin: 25px 0 15px 0;
        }}
        
        .risk-summary {{
            background: linear-gradient(135deg, {risk_color}15 0%, {risk_color}25 100%);
            border: 2px solid {risk_color};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .risk-score {{
            font-size: 3em;
            font-weight: bold;
            color: {risk_color};
            margin: 10px 0;
        }}
        
        .risk-level {{
            font-size: 1.5em;
            font-weight: bold;
            color: {risk_color};
            margin: 10px 0;
        }}
        
        .risk-matrix {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin: 20px 0;
            max-width: 600px;
        }}
        
        .risk-cell {{
            padding: 15px;
            text-align: center;
            border-radius: 8px;
            font-weight: bold;
            color: white;
            font-size: 0.9em;
        }}
        
        .risk-very-low {{ background-color: #28a745; }}
        .risk-low {{ background-color: #6f42c1; }}
        .risk-medium {{ background-color: #ffc107; color: #333; }}
        .risk-high {{ background-color: #fd7e14; }}
        .risk-very-high {{ background-color: #dc3545; }}
        
        .risk-item {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .treatment-plan {{
            background: #e8f5e8;
            border: 1px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .treatment-plan h4 {{
            color: #28a745;
            margin-bottom: 10px;
        }}
        
        .action-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            margin: 8px 0;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        .footer p {{
            margin: 5px 0;
            font-size: 0.9em;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company_name} 비즈니스 인텔리전스 리포트</h1>
            <div class="subtitle">2025년 8월 {company_name} 리스크 관리수준 종합분석</div>

        </div>
        
        <div class="content">
            <!-- 실행 요약 -->
            <div class="section">
                <h2>📊 실행 요약</h2>
                <div class="risk-summary">
                    <div class="risk-score">{overall_score:.1f}</div>
                    <div class="risk-level">{overall_level}</div>
                    <p>종합 리스크 점수 및 현재 리스크 레벨</p>
                </div>
                <p><strong>분석 대상:</strong> {company_name}</p>
                <p><strong>분석 일시:</strong> {current_date}</p>
                <p><strong>분석 방법:</strong> FinBERT 감성분석 + 키워드 분석</p>
            </div>
            
            <!-- 데이터 종합 분석 방법론 -->
            <div class="section">
                <h2>🔬 데이터 종합 분석 방법론</h2>
                <p>본 보고서는 다양한 데이터 소스를 종합적으로 분석하여 리스크를 평가합니다.</p>
                
                <h3>📰 뉴스 데이터 분석</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>분석 범위:</strong> 최근 14일간의 주요 뉴스 기사</p>
                    <p><strong>분석 방법:</strong> FinBERT 감성분석 + 리스크 키워드 검색</p>
                    <p><strong>데이터 소스:</strong> 주요 경제/금융 언론사, 전문 매체</p>
                    <p><strong>리스크 반영:</strong> 시장 동향, 규제 변화, 경쟁사 동향, 기술 혁신 등</p>
                </div>
                
                <h3>📱 소셜미디어 데이터 분석</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>분석 범위:</strong> Reddit, Stocktwits, Twitter 등 주요 소셜 플랫폼</p>
                    <p><strong>분석 방법:</strong> 실시간 감정 분석 + 리스크 키워드 모니터링</p>
                    <p><strong>데이터 소스:</strong> 투자자 커뮤니티, 전문가 의견, 일반 사용자 반응</p>
                    <p><strong>리스크 반영:</strong> 시장 심리, 투자자 신뢰도, 브랜드 평판 등</p>
                </div>
                
                <h3>📊 공시 데이터 분석</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>분석 범위:</strong> 최신 공시 정보 및 재무제표</p>
                    <p><strong>분석 방법:</strong> 규제 준수성 검토 + 재무 건전성 평가</p>
                    <p><strong>데이터 소스:</strong> DART(한국), SEC-API(미국) 등 공식 공시 시스템</p>
                    <p><strong>리스크 반영:</strong> 법적 리스크, 재무 리스크, 규제 리스크 등</p>
                </div>
                
                <h3>🤖 AI 기반 감성분석</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>분석 도구:</strong> FinBERT (금융 특화 감성분석 모델)</p>
                    <p><strong>분석 대상:</strong> 뉴스 제목, 기사 내용, 소셜미디어 게시글</p>
                    <p><strong>분석 결과:</strong> 긍정/부정/중립 감성 점수 (0~1 범위)</p>
                    <p><strong>리스크 반영:</strong> 시장 심리, 브랜드 평판, 투자자 신뢰도 등</p>
                </div>
                
                <h3>🔍 리스크 키워드 사전 분석</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>분석 방법:</strong> 100+ 리스크 키워드 사전 기반 패턴 매칭</p>
                    <p><strong>키워드 범주:</strong> 재무, 운영, 규제, 시장, 기술, 환경, 평판 리스크</p>
                    <p><strong>분석 결과:</strong> 키워드 히트 건수 및 종합 리스크 점수</p>
                    <p><strong>리스크 반영:</strong> 구체적인 리스크 요소 식별 및 분류</p>
                </div>
                
                <h3>📈 종합 리스크 평가</h3>
                <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #28a745;">
                    <p><strong>평가 방법:</strong> FinBERT 감성 지표 + 키워드 기반 리스크 시그널</p>
                    <p><strong>리스크 레벨:</strong> 매우 낮음(1-5) ~ 매우 높음(21-25)</p>
                    <p><strong>신뢰도:</strong> 다중 데이터 소스 교차 검증으로 높은 신뢰성 확보</p>
                </div>
            </div>
            
            <!-- 리스크 관리 프로세스 개요 -->
            <div class="section">
                <h2>🔄 리스크 관리 프로세스</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0;">
                    <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 10px;">
                        <h3>1. 식별</h3>
                        <p>리스크 요소 발견 및 분류</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #f3e5f5; border-radius: 10px;">
                        <h3>2. 분석</h3>
                        <p>확률과 영향도 평가</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #e8f5e8; border-radius: 10px;">
                        <h3>3. 평가</h3>
                        <p>리스크 수용 가능성 판단</p>
                    </div>
                    <div style="text-align: center; padding: 20px; background: #fff3e0; border-radius: 10px;">
                        <h3>4. 처리</h3>
                        <p>리스크 대응 전략 수립</p>
                    </div>
                </div>
            </div>
            
            <!-- 리스크 매트릭스 -->
            <div class="section">
                <h2>📈 리스크 매트릭스 (5x5)</h2>
                <div class="risk-matrix">
                    <div class="risk-cell risk-very-low">1</div>
                    <div class="risk-cell risk-very-low">2</div>
                    <div class="risk-cell risk-low">3</div>
                    <div class="risk-cell risk-low">4</div>
                    <div class="risk-cell risk-medium">5</div>
                    
                    <div class="risk-cell risk-very-low">2</div>
                    <div class="risk-cell risk-low">4</div>
                    <div class="risk-cell risk-low">6</div>
                    <div class="risk-cell risk-medium">8</div>
                    <div class="risk-cell risk-medium">10</div>
                    
                    <div class="risk-cell risk-low">3</div>
                    <div class="risk-cell risk-low">6</div>
                    <div class="risk-cell risk-medium">9</div>
                    <div class="risk-cell risk-medium">12</div>
                    <div class="risk-cell risk-high">15</div>
                    
                    <div class="risk-cell risk-low">4</div>
                    <div class="risk-cell risk-medium">8</div>
                    <div class="risk-cell risk-medium">12</div>
                    <div class="risk-cell risk-high">16</div>
                    <div class="risk-cell risk-high">20</div>
                    
                    <div class="risk-cell risk-medium">5</div>
                    <div class="risk-cell risk-medium">10</div>
                    <div class="risk-cell risk-high">15</div>
                    <div class="risk-cell risk-high">20</div>
                    <div class="risk-cell risk-very-high">25</div>
                </div>
                <p style="text-align: center; margin-top: 20px; color: #666;">
                    <strong>X축:</strong> 영향도 (1: 매우 낮음 ~ 5: 매우 높음) | 
                    <strong>Y축:</strong> 발생확률 (1: 매우 낮음 ~ 5: 매우 높음)
                </p>
            </div>
            
            <!-- 식별된 리스크 분석 -->
            <div class="section">
                <h2>🔍 식별된 리스크 분석</h2>
                <p>FinBERT 감성분석과 키워드 분석을 통해 식별된 주요 리스크 요소들입니다.</p>
                
                <h3>감성분석 결과</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>부정적 감성:</strong> {report['risk']['finbert']['neg']:.3f}</p>
                    <p><strong>중립적 감성:</strong> {report['risk']['finbert']['neu']:.3f}</p>
                    <p><strong>긍정적 감성:</strong> {report['risk']['finbert']['pos']:.3f}</p>
                </div>
                
                <h3>키워드 분석 결과</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 15px 0;">
                    <p><strong>발견된 리스크 키워드:</strong> {report['risk']['keyword_hits_total']}건</p>
                    <p><strong>종합 리스크 점수:</strong> {report['risk']['risk_score_0to1']:.3f} (0~1 범위)</p>
                </div>
                
                <h3>상세 리스크 항목</h3>"""
    
    # 식별된 리스크 항목들 추가
    for risk_item in risk_assessment[:10]:  # 상위 10개만 표시
        risk_id = risk_item.get("risk_id", "N/A")
        name = risk_item.get("name", "N/A")
        category = risk_item.get("category", "N/A")
        probability = risk_item.get("probability", 0)
        impact = risk_item.get("impact", 0)
        risk_score = risk_item.get("risk_score", 0)
        risk_level = risk_item.get("risk_level", "N/A")
        description = risk_item.get("description", "N/A")
        
        html += f"""
                <div class="risk-item">
                    <h4>{name}</h4>
                    <p><strong>카테고리:</strong> {category}</p>
                    <p><strong>발생확률:</strong> {probability}/5</p>
                    <p><strong>영향도:</strong> {impact}/5</p>
                    <p><strong>리스크 점수:</strong> {risk_score}</p>
                    <p><strong>리스크 레벨:</strong> {risk_level}</p>
                    <p><strong>설명:</strong> {description}</p>
                </div>"""
    
    html += """
            </div>
            
            <!-- 리스크 처리 계획 -->
            <div class="section">
                <h2>📋 리스크 처리 계획</h2>
                <p>리스크 처리 전략입니다.</p>"""
    
    # 리스크 처리 계획 추가
    for plan in treatment_plans[:5]:  # 상위 5개만 표시
        risk_id = plan.get("risk_id", "N/A")
        risk_name = plan.get("risk_name", "N/A")
        target_level = plan.get("target_level", "N/A")
        strategy = plan.get("strategy", "N/A")
        timeline = plan.get("timeline", "N/A")
        resources = plan.get("resources", "N/A")
        
        html += f"""
                <div class="treatment-plan">
                    <h4>{risk_name}</h4>
                    <p><strong>목표 리스크 레벨:</strong> {target_level}</p>
                    <p><strong>처리 전략:</strong> {strategy}</p>
                    <p><strong>예상 소요시간:</strong> {timeline}</p>
                    <p><strong>필요 자원:</strong> {resources}</p>
                </div>"""
    
    html += """
            </div>
            
            <!-- 모니터링 및 후속조치 -->
            <div class="section">
                <h2>📊 모니터링 및 후속조치</h2>
                <h3>정기 모니터링</h3>
                <ul style="margin-left: 20px;">
                    <li>월간 리스크 지표 점검</li>
                    <li>분기별 리스크 대응 효과성 평가</li>
                    <li>연간 리스크 관리 체계 검토</li>
                </ul>
                
                <h3>긴급 대응 절차</h3>
                <ul style="margin-left: 20px;">
                    <li>리스크 발생 시 즉시 보고 체계</li>
                    <li>비상 대응팀 구성 및 운영</li>
                    <li>리스크 대응 결과 문서화</li>
                </ul>
            </div>
            
            <!-- 비즈니스 전망 -->
            <div class="section">
                <h2>🚀 비즈니스 전망</h2>
                <p>현재 리스크 분석 결과를 바탕으로 한 비즈니스 전망입니다.</p>
                
                <h3>긍정적 요인</h3>
                <ul style="margin-left: 20px;">
                    <li>리스크 관리 체계의 체계적 운영</li>
                    <li>ISO 31000 표준 준수로 인한 신뢰도 향상</li>
                    <li>지속적인 리스크 모니터링 및 대응</li>
                </ul>
                
                <h3>주의 요인</h3>
                <ul style="margin-left: 20px;">
                    <li>외부 환경 변화에 따른 새로운 리스크 요소</li>
                    <li>리스크 대응 전략의 효과성 지속적 검증 필요</li>
                    <li>조직 내 리스크 인식 문화 정착</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>본 보고서는 AI 분석 도구를 활용해 자동 생성되었습니다.</strong></p>
            <p>분석 일시: """ + current_date + """</p>
            <p>분석 도구: FinBERT + 키워드 분석 + Python</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def html_to_pdf_weasy(html_str: str, pdf_path: Path):
    HTML(string=html_str).write_pdf(str(pdf_path), stylesheets=[
        CSS(string="@page { size: A4; margin: 14mm; }")
    ])

def html_to_pdf_reportlab(html_str: str, pdf_path: Path, chart_b64: Optional[str] = None):
    # 매우 심플한 폴백(문단/표 일부만): 핵심 텍스트 위주
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # 타이틀
    story.append(Paragraph("회사 리스크 & 인텔리전스 리포트", styles["Title"]))
    story.append(Spacer(1, 6))

    # chart 이미지 삽입(가능한 경우)
    if chart_b64:
        img = ImageReader(BytesIO(base64.b64decode(chart_b64)))
        story.append(RLImage(img, width=280, height=200))
        story.append(Spacer(1, 8))

    # 아주 단순한 텍스트 파싱
    import bs4
    soup = bs4.BeautifulSoup(html_str, "html.parser")
    # 섹션 타이틀/테이블 간단 추출
    for h2 in soup.find_all(["h2"]):
        story.append(Paragraph(h2.get_text(), styles["Heading2"]))
        # 해당 섹션의 첫 번째 테이블만 옮김
        tbl = h2.find_next("table")
        if tbl:
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["th","td"])]
                rows.append(cells)
            t = Table(rows, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
                ("BOX", (0,0), (-1,-1), 0.25, colors.grey),
                ("INNERGRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
    doc.build(story)

def generate_pdf(report: Dict[str, Any], outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    base = report["_base_id"]
    html_str = render_html(report)
    html_path = outdir / f"{base}.html"
    pdf_path = outdir / f"{base}.pdf"
    html_path.write_text(html_str, encoding="utf-8")

    # WeasyPrint 우선
    if WEASYPRINT_AVAILABLE:
        try:
            html_to_pdf_weasy(html_str, pdf_path)
            return pdf_path
        except Exception:
            pass

    # ReportLab 폴백
    if REPORTLAB_AVAILABLE:
        try:
            chart_b64 = re.search(r"base64,([A-Za-z0-9+/=]+)", html_str)
            chart_b64 = chart_b64.group(1) if chart_b64 else None
            html_to_pdf_reportlab(html_str, pdf_path, chart_b64)
            return pdf_path
        except Exception:
            pass

    # 둘 다 실패한 경우 HTML만 남김
    return html_path

# ---------------------------
# CLI
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="회사명/홈페이지 → 공시·뉴스·SNS·리스크 + PDF")
    parser.add_argument("--name", type=str, help="회사명 (예: 삼성전자)")
    parser.add_argument("--url", type=str, help="홈페이지 URL (예: https://www.samsung.com)")
    parser.add_argument("--country", type=str, default=None, help="국가 힌트 (KR/US/...) — KR이면 DART 공시 시도")
    parser.add_argument("--lang", type=str, default="ko", help="뉴스 언어(ko/en 등)")
    parser.add_argument("--outdir", type=str, default=str(REPORT_DIR), help="리포트 저장 디렉토리")
    parser.add_argument("--use-serpapi", action="store_true", help="SerpApi 사용 (가능할 때 RSS보다 우선)")
    parser.add_argument("--serpapi-key", type=str, default=os.getenv("SERPAPI_API_KEY"), help="SerpApi API Key (미지정 시 환경변수 SERPAPI_API_KEY 사용)")
    # SEC 필터 옵션
    parser.add_argument("--ticker", type=str, default=None, help="SEC 티커 (미국 상장사)")
    parser.add_argument("--cik", type=str, default=None, help="SEC CIK")
    parser.add_argument("--forms", type=str, default=None, help="SEC 폼타입 콤마 구분 (예: 10-K,10-Q,8-K)")
    parser.add_argument("--from-date", type=str, default=None, help="SEC 검색 시작일 YYYY-MM-DD")
    parser.add_argument("--to-date", type=str, default=None, help="SEC 검색 종료일 YYYY-MM-DD")
    # ISO 갭분석 맞춤형 분석
    parser.add_argument("--iso-focus", type=str, default=None, help="집중 분석할 ISO 표준 콤마구분 (예: 9001,14001,45001)")
    parser.add_argument("--output-format", type=str, default="html", help="출력 형식: html 또는 json")
    args = parser.parse_args()

    # ISO 포커스 표준 파싱
    iso_focus_standards = []
    if args.iso_focus:
        iso_focus_standards = [s.strip() for s in args.iso_focus.split(',')]
    
    report = build_report(
        args.name,
        args.url,
        args.country,
        args.lang,
        use_serpapi=args.use_serpapi,
        serpapi_key=args.serpapi_key,
        sec_ticker=args.ticker,
        sec_cik=args.cik,
        sec_forms=args.forms,
        sec_from_date=args.from_date,
        sec_to_date=args.to_date,
        iso_focus=iso_focus_standards,
        output_format=args.output_format
    )
    
    # 출력 형식에 따른 처리
    if args.output_format == 'json':
        # JSON 형식으로 출력
        import json
        gap_analysis_result = {
            'overall_score': report.get('iso_assessment', {}).get('overall_score', 0),
            'iso_recommendation': report.get('iso_recommendation', {}),
            'key_risks': [],
            'recommendations': [],
            'report_path': '',
            'analysis_details': {
                'iso_assessment': report.get('iso_assessment', {}),
                'baseline_risk_analysis': report.get('baseline_risk_analysis', {}),
                'chatgpt_enhanced_analysis': report.get('chatgpt_enhanced_analysis', {})
            }
        }
        
        # 키 리스크 추출
        if 'baseline_risk_analysis' in report:
            baseline = report['baseline_risk_analysis']
            gap_analysis_result['key_risks'] = baseline.get('key_findings', [])[:5]  # 상위 5개
            
        # 권장사항 추출  
        if 'iso_recommendation' in report and report['iso_recommendation']:
            rec = report['iso_recommendation']
            gap_analysis_result['recommendations'] = rec.get('next_steps', [])[:3]  # 상위 3개
            
        print(json.dumps(gap_analysis_result, ensure_ascii=False, indent=2))
        return
    
    # HTML 형식 (기본)
    outpath = generate_pdf(report, Path(args.outdir))

    print("\n=== 리포트 생성 완료 ===")
    print(f"파일: {outpath.resolve()}")
    print(f"데이터 JSON: {(DATA_DIR / (report['_base_id'] + '.json')).resolve()}")

    # ISO 31000 보고서 비활성화 (생성하지 않음)
    
    # ChatGPT AI 지능형 분석보고서 생성
    generate_chatgpt_enhanced_report(report, Path(args.outdir))
    
    # 통합 종합 분석보고서 생성
    generate_integrated_report(report, Path(args.outdir))

def generate_chatgpt_html_report(report: Dict[str, Any], chatgpt_data: Dict[str, Any]) -> str:
    """ChatGPT API를 활용한 지능형 HTML 보고서 생성"""
    
    company_name = report['entity'].get('name') or report['entity'].get('domain') or 'Unknown'
    current_date = dt.datetime.now().strftime("%Y년 %m월 %d일")
    
    # ChatGPT 분석 결과에서 주요 데이터 추출
    contextual_analysis = chatgpt_data.get("contextual_analysis", {})
    risk_scenarios = chatgpt_data.get("risk_scenarios", [])
    personalized_reports = chatgpt_data.get("personalized_reports", {})
    
    def format_list(items):
        """리스트를 HTML 형식으로 변환"""
        if not items:
            return "<p>항목이 없습니다.</p>"
        
        html_items = []
        for item in items:
            html_items.append(f"<li>{item}</li>")
        
        return f"<ul>{''.join(html_items)}</ul>"
    
    def format_risk_scenarios(scenarios):
        """리스크 시나리오를 HTML 형식으로 변환 (점수/근거/정렬/배지 포함)"""
        if not scenarios:
            return "<p>리스크 시나리오가 생성되지 않았습니다.</p>"
        # 증거 매핑: 뉴스 N1.., 공시 F1.. (상위 스코프 데이터 참조)
        evidence_map: Dict[str, Dict[str, str]] = {}
        for idx, n in enumerate(report.get('news', [])[:10], start=1):
            evidence_map[f"N{idx}"] = {"title": n.get('title') or '뉴스', "url": n.get('url') or '#'}
        for idx, f in enumerate(report.get('filings', [])[:10], start=1):
            evidence_map[f"F{idx}"] = {"title": f.get('title') or f.get('type') or '공시', "url": f.get('url') or '#'}
        # 이전 시나리오 제목(신규 배지)
        prev_titles = set(report.get('previous_scenario_titles', [])) if isinstance(report, dict) else set()
        # 문자열→수치 매핑
        prob_map = {"매우 높음":5, "높음":4, "보통":3, "낮음":2, "매우 낮음":1}
        impact_map = {"매우 높음":5, "높음":4, "보통":3, "낮음":2, "매우 낮음":1}
        def score_of(s: Dict[str, Any]) -> int:
            ln = s.get('likelihood_num') or prob_map.get(s.get('probability',''), 0)
            im = s.get('impact_num') or impact_map.get(s.get('impact',''), 0)
            try:
                return int(ln) * int(im)
            except Exception:
                return 0
        # 정렬 및 TOP3
        scenarios_sorted = sorted(scenarios, key=score_of, reverse=True)
        html_scenarios = []
        for i, scenario in enumerate(scenarios_sorted):
            risk_class = f"risk-{scenario.get('risk_level', 'medium').lower().replace(' ', '-')}"
            badge_top = '<span class="risk-level-badge risk-high">TOP</span>' if i < 3 else ''
            cat = scenario.get('category') or ''
            # evidence 링크들
            ev = scenario.get('evidence') or []
            ev_links = []
            for eid in ev[:5]:
                meta = evidence_map.get(str(eid))
                if meta:
                    ev_links.append(f"<a href=\"{meta['url']}\" target=\"_blank\">{eid}</a>")
            ev_html = (' '.join(ev_links)) if ev_links else ''
            # 신규 배지
            is_new = scenario.get('title') not in prev_titles
            new_badge = '<span class="risk-level-badge risk-medium">신규</span>' if is_new else ''
            # 점수
            sc = score_of(scenario)
            html_scenarios.append(f"""
            <div class="scenario-card">
                <div class="scenario-title">{scenario.get('title', '제목 없음')} {badge_top} {new_badge}</div>
                <p><strong>카테고리:</strong> {cat or '알 수 없음'} | <strong>점수:</strong> {sc}</p>
                <p><strong>설명:</strong> {scenario.get('description', '설명 없음')}</p>
                <p><strong>발생 확률:</strong> {scenario.get('probability', '알 수 없음')} (<em>{scenario.get('likelihood_num','-')}</em>)</p>
                <p><strong>영향도:</strong> {scenario.get('impact', '알 수 없음')} (<em>{scenario.get('impact_num','-')}</em>)</p>
                <span class="risk-level-badge {risk_class}">{scenario.get('risk_level', '알 수 없음')}</span>
                <p><strong>예상 발생 시점:</strong> {scenario.get('timeline', '알 수 없음')} | <strong>시간지평:</strong> {scenario.get('horizon','-')}</p>
                <p><strong>예측 신뢰도:</strong> {scenario.get('confidence', '알 수 없음')}</p>
                <p><strong>근거:</strong> {ev_html}</p>
                <h4>발생 트리거:</h4>
                {format_list(scenario.get('triggers', []))}
                <h4>대응 전략:</h4>
                {format_list(scenario.get('mitigation_strategies', []))}
            </div>
            """)
        return ''.join(html_scenarios)
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} AI 지능형 비즈니스 인텔리전스 리포트 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .ai-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .section h3 {{
            color: #764ba2;
            font-size: 1.4em;
            margin: 25px 0 15px 0;
        }}
        
        .ai-insight {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba225 100%);
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }}
        
        .scenario-card {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
        }}
        
        .scenario-title {{
            color: #667eea;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .risk-level-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 5px;
        }}
        
        .risk-very-high {{ background-color: #dc3545; color: white; }}
        .risk-high {{ background-color: #fd7e14; color: white; }}
        .risk-medium {{ background-color: #ffc107; color: #333; }}
        .risk-low {{ background-color: #6f42c1; color: white; }}
        .risk-very-low {{ background-color: #28a745; color: white; }}
        
        .relevance-high {{
            background-color: #28a745;
            color: white;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            font-weight: bold;
        }}
        
        .relevance-medium {{
            background-color: #ffc107;
            color: #212529;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.7em;
            font-weight: bold;
        }}
        
        .personalized-report {{
            background: #e8f5e8;
            border: 1px solid #28a745;
            border-radius: 10px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{company_name} AI 지능형 비즈니스 인텔리전스 리포트</h1>
            <div class="subtitle">2025년 8월 {company_name} AI 기반 종합 리스크 분석</div>
            <div class="ai-badge">🤖 GPT-4o-mini AI 분석</div>
        </div>
        
        <div class="content">
            <!-- 실행 요약 -->
            <div class="section">
                <h2>🚀 AI 실행 요약</h2>
                <div class="ai-insight">
                    <p><strong>AI 분석 모델:</strong> OpenAI GPT-4o-mini</p>
                    <p><strong>분석 대상:</strong> {company_name}</p>
                    <p><strong>분석 일시:</strong> {current_date}</p>
                    <p><strong>AI 분석 방법:</strong> 맥락적 데이터 해석 + 리스크 시나리오 생성 + 맞춤형 보고서</p>
                    <p><strong>기존 시스템 통합:</strong> FinBERT + 키워드 분석 + ChatGPT AI</p>
                </div>
            </div>
            
            <!-- AI 맥락적 분석 -->
            <div class="section">
                <h2>🔍 AI 맥락적 리스크 분석</h2>
                
                <h3>🎯 숨겨진 리스크 요소</h3>
                <div class="ai-insight">
                    {format_list(contextual_analysis.get('hidden_risks', ['분석 데이터가 부족합니다.']))}
                </div>
                
                <h3>📊 시장 맥락 및 트렌드</h3>
                <div class="ai-insight">
                    <p>{contextual_analysis.get('market_context', '시장 맥락 분석을 위해 추가 데이터가 필요합니다.')}</p>
                </div>
                
                <h3>🏆 경쟁사 동향 분석</h3>
                <div class="ai-insight">
                    <p>{contextual_analysis.get('competitive_analysis', '경쟁사 분석을 위해 추가 데이터가 필요합니다.')}</p>
                </div>
                
                <h3>⚖️ 규제 환경 변화</h3>
                <div class="ai-insight">
                    <p>{contextual_analysis.get('regulatory_implications', '규제 환경 분석을 위해 추가 데이터가 필요합니다.')}</p>
                </div>
                
                <h3>💹 투자자 심리 및 시장 신뢰도</h3>
                <div class="ai-insight">
                    <p>{contextual_analysis.get('investor_sentiment', '투자자 심리 분석을 위해 추가 데이터가 필요합니다.')}</p>
                </div>
                
                <h3>💡 AI 권장사항</h3>
                <div class="ai-insight">
                    {format_list(contextual_analysis.get('recommendations', ['구체적인 권장사항을 위해 추가 분석이 필요합니다.']))}
                </div>
            </div>
            
            <!-- AI 리스크 시나리오 -->
            <div class="section">
                <h2>🔮 AI 생성 리스크 시나리오</h2>
                <p>ChatGPT AI가 현재 데이터를 바탕으로 향후 6개월 내 발생 가능한 리스크 시나리오를 생성했습니다.</p>
                
                {format_risk_scenarios(risk_scenarios) if risk_scenarios else '<p>AI 리스크 시나리오 생성 중 오류가 발생했습니다. 기본 리스크 시나리오를 제공합니다.</p>'}
            </div>
            
            <!-- 맞춤형 보고서 -->
            <div class="section">
                <h2>📋 AI 맞춤형 분석 보고서</h2>
                
                <h3>👔 경영진용 맞춤 보고서</h3>
                <div class="personalized-report">
                    <p>{personalized_reports.get('executive', '경영진용 보고서 생성 중 오류가 발생했습니다.')}</p>
                </div>
                
                <h3>💰 투자자용 맞춤 보고서</h3>
                <div class="personalized-report">
                    <p>{personalized_reports.get('investor', '투자자용 보고서 생성 중 오류가 발생했습니다.')}</p>
                </div>
            </div>
            
            <!-- AI 분석 방법론 -->
            <div class="section">
                <h2>🤖 AI 분석 방법론</h2>
                
                <h3>🧠 GPT-4o-mini 모델 특징</h3>
                <div class="ai-insight">
                    <p><strong>맥락 이해:</strong> 단순 키워드 매칭을 넘어서 문맥적 의미 파악</p>
                    <p><strong>시나리오 생성:</strong> 현재 데이터를 바탕으로 미래 리스크 시나리오 예측</p>
                    <p><strong>맞춤형 해석:</strong> 사용자 프로필에 따른 맞춤형 분석 및 권장사항</p>
                    <p><strong>실시간 학습:</strong> 새로운 데이터에 대한 적응적 분석</p>
                </div>
                
                <h3>📈 기존 시스템과의 통합</h3>
                <div class="ai-insight">
                    
                    <p><strong>FinBERT:</strong> 금융 특화 감성분석</p>
                    <p><strong>키워드 분석:</strong> 리스크 사전 기반 패턴 매칭</p>
                    <p><strong>ChatGPT AI:</strong> 지능형 맥락 분석 및 시나리오 생성</p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>본 보고서는 OpenAI GPT-4o-mini AI 모델을 활용하여 생성되었습니다.</p>
            <p>© 2025 AI Enhanced Business Intelligence System</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def generate_integrated_report(report: Dict[str, Any], outdir: Path) -> Path:
    """AI 분석을 통합한 종합 분석보고서 생성 (ISO 31000 제거)"""
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        base = report["_base_id"]
        integrated_path = outdir / f"{base}_통합종합분석보고서_2025.html"
        
        integrated_html_content = generate_integrated_html_report(report)
        
        with open(integrated_path, "w", encoding="utf-8") as f:
            f.write(integrated_html_content)
        print(f"[OK] 통합 종합 분석보고서 생성 완료: {integrated_path}")
        return integrated_path
    except Exception as e:
        print(f"❌ 통합 보고서 생성 중 오류 발생: {e}")
        return None

def markdown_to_html(markdown_text: str) -> str:
    """간단한 마크다운을 HTML로 변환"""
    if not markdown_text:
        return ""
    
    html = markdown_text
    
    # 헤딩 변환
    html = re.sub(r'^# (.+)$', r'<h2 class="md-title">\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h3 class="md-subtitle">\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h4 class="md-subheading">\1</h4>', html, flags=re.MULTILINE)
    
    # 볼드 텍스트 변환 (** 또는 __ 형식)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
    
    # 리스트 변환 (- 로 시작하는 줄들)
    lines = html.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result_lines.append('<ul class="md-list">')
                in_list = True
            list_item = line.strip()[2:].strip()  # '- ' 제거
            result_lines.append(f'  <li class="md-list-item">{list_item}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            if line.strip():  # 빈 줄이 아닌 경우만
                result_lines.append(f'<p class="md-paragraph">{line.strip()}</p>')
            else:
                result_lines.append('<br>')
    
    # 리스트가 끝나지 않은 경우 닫기
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)

def generate_integrated_html_report(report: Dict[str, Any]) -> str:
    """AI 분석 기반 통합 HTML 보고서 생성 (ISO 31000 제거)."""
    
    company_name = report['entity'].get('name') or report['entity'].get('domain') or 'Unknown'
    current_date = dt.datetime.now().strftime("%Y년 %m월 %d일")
    
    # 기존 데이터
    news = report.get("news", [])
    social_media = report.get("social_media", [])
    filings = report.get("filings", [])
    risk_data = report.get("risk", {})
    
    # ISO 31000 제거: 기존 필드 대신 baseline 결과 사용
    baseline_data = report.get("baseline_risk_analysis", {})
    
    # ChatGPT AI 데이터 - 최신 분석 결과 직접 사용
    chatgpt_data = report.get("chatgpt_enhanced_analysis", {})
    
    # AI 리스크 시나리오 데이터 직접 추출
    ai_risk_scenarios = []
    if chatgpt_data and 'risk_scenarios' in chatgpt_data:
        ai_risk_scenarios = chatgpt_data['risk_scenarios']
    elif 'risk_scenarios' in report:
        ai_risk_scenarios = report['risk_scenarios']
    
    # AI 맥락적 분석 데이터 직접 추출
    ai_contextual_analysis = {}
    if chatgpt_data and 'contextual_analysis' in chatgpt_data:
        ai_contextual_analysis = chatgpt_data['contextual_analysis']
    elif 'contextual_analysis' in report:
        ai_contextual_analysis = report['contextual_analysis']
    
    # AI 맞춤형 보고서 데이터 직접 추출
    ai_personalized_reports = {}
    if chatgpt_data and 'personalized_reports' in chatgpt_data:
        ai_personalized_reports = chatgpt_data['personalized_reports']
    elif 'personalized_reports' in report:
        ai_personalized_reports = report['personalized_reports']
    
    # FinBERT 데이터 안전하게 추출
    finbert_data = risk_data.get('finbert', {})
    if not finbert_data:
        finbert_data = {
            'pos': '데이터 없음',
            'neg': '데이터 없음',
            'neu': '데이터 없음'
        }
    
    # 키워드 히트 데이터 안전하게 추출
    keyword_hits = risk_data.get('keyword_hits', {})
    keyword_hits_total = risk_data.get('keyword_hits_total', 0)
    if not keyword_hits:
        keyword_hits = {'리스크 키워드': '데이터 없음'}
        keyword_hits_total = '데이터 없음'
    
    # 리스크 점수 및 색상 - 데이터 일관성 개선
    risk_score = risk_data.get("risk_score_0to1", 0)
    if isinstance(risk_score, str):
        try:
            risk_score = float(risk_score)
        except:
            risk_score = 0.5
    
    # ISO 31000 제거: FinBERT 점수를 그대로 사용
    integrated_risk_score = risk_score
    
    # 리스크 레벨 판정 기준 명확화
    if integrated_risk_score <= 0.2:
        risk_color = "#28a745"  # 녹색
        risk_level = "매우 낮음"
    elif integrated_risk_score <= 0.4:
        risk_color = "#6f42c1"  # 보라색
        risk_level = "낮음"
    elif integrated_risk_score <= 0.6:
        risk_color = "#ffc107"  # 노란색
        risk_level = "보통"
    elif integrated_risk_score <= 0.8:
        risk_color = "#fd7e14"  # 주황색
        risk_level = "높음"
    else:
        risk_color = "#dc3545"  # 빨간색
        risk_level = "매우 높음"

    # SerpApi 데이터 추출
    serpapi_data = report.get('serpapi', {}) or {}
    serpapi_ai_overview = serpapi_data.get('ai_overview') or {}
    serpapi_related_questions = serpapi_data.get('related_questions') or []
    serpapi_trends = serpapi_data.get('trends') or {}
    serpapi_youtube = serpapi_data.get('youtube') or []
    serpapi_naver = serpapi_data.get('naver') or []
    serpapi_patents = serpapi_data.get('patents') or []

    # SerpApi Trends 포맷팅
    def format_trends(trends_obj: Dict[str, Any]) -> str:
        try:
            # 에러가 있는 경우
            if trends_obj.get("error"):
                return f'<p>경고: {trends_obj["error"]}</p>'
            
            iot = trends_obj.get('interest_over_time', {})
            timeline = iot.get('timeline_data', []) or trends_obj.get('timeline_data', [])
            if not timeline:
                # Fallback: 최근 뉴스 발행일 카운트로 대체
                counts: Dict[str, int] = {}
                for n in news[:20]:
                    pub = (n.get('published') or '')[:10]
                    if pub:
                        counts[pub] = counts.get(pub, 0) + 1
                if not counts:
                    return ''
                rows = []
                for d in sorted(counts.keys())[-8:]:
                    rows.append(f"<tr><td class=\"nowrap\">{d}</td><td>{counts[d]}</td></tr>")
                return '<table><tr><th class="nowrap">날짜</th><th>뉴스 건수</th></tr>' + ''.join(rows) + '</table>'
            
            rows = []
            for pt in timeline[-8:]:
                date = pt.get('date') or pt.get('formattedTime') or ''
                value = None
                if isinstance(pt.get('values'), list) and pt['values']:
                    value = pt['values'][0].get('value')
                value = value if value is not None else pt.get('value')
                rows.append(f"<tr><td class=\"nowrap\">{date}</td><td>{value}</td></tr>")
            
            return '<table><tr><th class="nowrap">날짜</th><th>관심도</th></tr>' + ''.join(rows) + '</table>'
        except Exception as e:
            return f'<p>경고: 트렌드 데이터 처리 중 오류: {str(e)}</p>'

    # SerpApi AI Overview 포맷팅
    def format_ai_overview(aio: Dict[str, Any]) -> str:
        # 에러 또는 데이터 없음 → ChatGPT 맥락 요약으로 대체
        if not aio or aio.get("error"):
            mc = ai_contextual_analysis.get('market_context') if isinstance(ai_contextual_analysis, dict) else None
            return f"<div class=\"ai-insight\"><p>{mc}</p></div>" if mc else ''
        text = aio.get('answer') or aio.get('summary') or aio.get('content')
        if not text:
            mc = ai_contextual_analysis.get('market_context') if isinstance(ai_contextual_analysis, dict) else None
            return f"<div class=\"ai-insight\"><p>{mc}</p></div>" if mc else ''
        source = aio.get('source', '')
        source_info = f'<small><em>출처: {source}</em></small>' if source else ''
        return f"<div class=\"ai-insight\"><p>{text}</p>{source_info}</div>"

    # SerpApi PAA 포맷팅
    def format_paa(items: List[Dict[str, Any]]) -> str:
        if isinstance(items, dict) and items.get("error"):
            items = []
        # 폴백: FAQ 생성 + 간단 답변(뉴스/요약 기반)
        if not items:
            faqs = [
                f"{company_name} 신제품 출시 일정은?",
                f"{company_name}의 최근 리콜/품질 이슈는?",
                f"{company_name}의 개인정보/보안 정책은?",
                f"{company_name}의 반독점/규제 이슈 현황은?",
                f"{company_name}의 서비스/구독 수익 동향은?"
            ]
            def answer_stub(q: str) -> str:
                # 뉴스 첫 1-2개에서 힌트 추출
                hints = []
                for n in news[:2]:
                    if n.get('title'): hints.append(n['title'])
                hint = ('; '.join(hints))[:160]
                return hint or "관련 최신 뉴스 기반 답변 생성 필요"
            lis = []
            for q in faqs:
                lis.append(f"<li><strong>{q}</strong><br/><small>{answer_stub(q)}</small></li>")
            return '<ul>' + ''.join(lis) + '</ul>'
        lis = []
        for it in items[:8]:
            q = it.get('question') or ''
            lnk = it.get('link') or '#'
            snippet = it.get('snippet', '')
            if snippet and snippet != "관련 검색어":
                lis.append(f"<li><a href=\"{lnk}\" target=\"_blank\">{q}</a><br/><small>{snippet}</small></li>")
            else:
                lis.append(f"<li><a href=\"{lnk}\" target=\"_blank\">{q}</a></li>")
        return '<ul>' + ''.join(lis) + '</ul>'

    # SerpApi YouTube 포맷팅
    def format_youtube(items: List[Dict[str, Any]]) -> str:
        if not items:
            # 뉴스에서 YouTube 링크 추출하여 대체
            yt = []
            for n in news[:20]:
                u = (n.get('url') or '')
                if 'youtube.com' in u or 'youtu.be' in u:
                    yt.append({"title": n.get('title','제목 없음'), "url": u, "views": '', "published": ''})
            items = yt
            if not items:
                return ''
        
        # 에러가 있는 경우
        if isinstance(items, dict) and items.get("error"):
            return f'<p>경고: {items["error"]}</p>'
        
        rows = []
        for v in items[:6]:
            title = v.get('title') or '제목 없음'
            url = v.get('url') or '#'
            views = v.get('views') or ''
            published = v.get('published') or ''
            rows.append(f"<tr><td class=\"nowrap\">{published}</td><td><a href=\"{url}\" target=\"_blank\">{title}</a></td><td>{views}</td></tr>")
        return '<table><tr><th class="nowrap">게시</th><th>제목</th><th>조회수</th></tr>' + ''.join(rows) + '</table>'

    # SerpApi Naver 포맷팅
    def format_naver(items: List[Dict[str, Any]]) -> str:
        if not items:
            return '<p>데이터 없음</p>'
        
        # 에러가 있는 경우
        if isinstance(items, dict) and items.get("error"):
            return f'<p>경고: {items["error"]}</p>'
        
        rows = []
        for n in items[:8]:
            title = n.get('title') or '제목 없음'
            url = n.get('url') or '#'
            snip = n.get('excerpt') or ''
            rows.append(f"<tr><td><a href=\"{url}\" target=\"_blank\">{title}</a></td><td>{snip}</td></tr>")
        return '<table><tr><th>제목</th><th>요약</th></tr>' + ''.join(rows) + '</table>'

    # SerpApi Patents 포맷팅
    def format_patents(patents_data: Dict[str, Any]) -> str:
        """특허 데이터를 HTML로 포맷팅"""
        if not patents_data or "error" in patents_data:
            error_msg = patents_data.get("error", "데이터 없음") if patents_data else "데이터 없음"
            return f'<div class="no-data"><p>경고: {error_msg}</p></div>'
        
        patents = patents_data.get("patents", [])
        if not patents:
            return '<div class="no-data"><p>📋 수집된 특허 데이터가 없습니다.</p></div>'
        
        html = '<table><tr><th>특허/문서</th><th>요약</th><th>관련성</th></tr>'
        
        for patent in patents:
            title = patent.get("title", "제목 없음")
            summary = patent.get("summary", "요약 없음")
            relevance = patent.get("relevance", "보통")
            
            # 관련성에 따른 배지 스타일
            relevance_class = "relevance-high" if relevance == "높음" else "relevance-medium"
            
            html += f'<tr><td><a href="#" target="_blank">{title}</a></td><td>{summary}</td><td><span class="{relevance_class}">{relevance}</span></td></tr>'
        
        html += '</table>'
        return html
    
    def format_list(items):
        if not items: return "<p>항목이 없습니다.</p>"
        html_items = [f"<li>{item}</li>" for item in items]
        return f"<ul>{''.join(html_items)}</ul>"
    
    def format_risk_scenarios(scenarios):
        if not scenarios: return "<p>리스크 시나리오가 생성되지 않았습니다.</p>"
        html_scenarios = []
        for scenario in scenarios:
            risk_class = f"risk-{scenario.get('risk_level', 'medium').lower().replace(' ', '-')}"
            html_scenarios.append(f"""
            <div class="scenario-card">
                <div class="scenario-title">{scenario.get('title', '제목 없음')}</div>
                <p><strong>설명:</strong> {scenario.get('description', '설명 없음')}</p>
                <p><strong>발생 확률:</strong> {scenario.get('probability', '알 수 없음')}</p>
                <p><strong>영향도:</strong> {scenario.get('impact', '알 수 없음')}</p>
                <span class="risk-level-badge {risk_class}">{scenario.get('risk_level', '알 수 없음')}</span>
                <p><strong>예상 발생 시점:</strong> {scenario.get('timeline', '알 수 없음')}</p>
                <p><strong>예측 신뢰도:</strong> {scenario.get('confidence', '알 수 없음')}</p>
                <h4>발생 트리거:</h4>{format_list(scenario.get('triggers', []))}
                <h4>대응 전략:</h4>{format_list(scenario.get('mitigation_strategies', []))}
            </div>
            """)
        return ''.join(html_scenarios)
    

    

    
    html = f"""<!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{company_name} 통합 종합 분석보고서 2025</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 30px rgba(0,0,0,0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                text-align: center;
                padding: 60px 30px;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
                opacity: 0.3;
            }}
            
            .header h1 {{
                font-size: 3em;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                font-weight: 700;
            }}
            
            .subtitle {{
                font-size: 1.4em;
                opacity: 0.9;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
            }}
            
            .badge-container {{
                display: flex;
                justify-content: center;
                gap: 15px;
                flex-wrap: wrap;
                margin-top: 20px;
                position: relative;
                z-index: 1;
            }}
            
            .badge {{
                display: inline-block;
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 0.9em;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            
            
            .badge-ai {{
                background: #6f42c1;
                color: white;
            }}
            
            .badge-integrated {{
                background: #fd7e14;
                color: white;
            }}
            
            .content {{
                padding: 40px 30px;
            }}
            
            .section {{
                margin-bottom: 40px;
                padding: 30px;
                background: white;
                border-radius: 15px;
                border-left: 5px solid #1e3c72;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .section:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 25px rgba(0,0,0,0.12);
            }}
            
            .section h2 {{
                color: #1e3c72;
                font-size: 2em;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 3px solid #e9ecef;
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .section h3 {{
                color: #2a5298;
                font-size: 1.5em;
                margin: 25px 0 15px 0;
                padding-left: 15px;
                border-left: 4px solid #007bff;
            }}
            
            .section h4 {{
                color: #495057;
                font-size: 1.2em;
                margin: 20px 0 10px 0;
            }}
            
            .risk-summary {{
                background: linear-gradient(135deg, {risk_color}15 0%, {risk_color}25 100%);
                border: 3px solid {risk_color};
                border-radius: 20px;
                padding: 30px;
                margin: 25px 0;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .risk-summary::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, {risk_color}10 0%, transparent 70%);
                animation: pulse 3s infinite;
            }}
            
            @keyframes pulse {{
                0% {{ transform: scale(1); opacity: 0.5; }}
                50% {{ transform: scale(1.1); opacity: 0.3; }}
                100% {{ transform: scale(1); opacity: 0.5; }}
            }}
            
            .risk-score {{
                font-size: 4em;
                font-weight: bold;
                color: {risk_color};
                margin: 15px 0;
                position: relative;
                z-index: 1;
            }}
            
            .risk-level {{
                font-size: 1.8em;
                font-weight: bold;
                color: {risk_color};
                margin: 15px 0;
                position: relative;
                z-index: 1;
            }}
            
            .risk-matrix {{
                margin: 25px 0;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .risk-cell {{
                padding: 20px 15px;
                text-align: center;
                border-radius: 10px;
                font-weight: bold;
                color: white;
                font-size: 0.9em;
                transition: transform 0.2s ease;
            }}
            
            .risk-cell:hover {{
                transform: scale(1.05);
            }}
            
            .risk-very-low {{ background-color: #28a745; }}
            .risk-low {{ background-color: #6f42c1; }}
            .risk-medium {{ background-color: #ffc107; color: #333; }}
            .risk-high {{ background-color: #fd7e14; }}
            .risk-very-high {{ background-color: #dc3545; }}
            
            /* 새로운 동적 매트릭스 스타일 - 가독성 개선 */
            .risk-matrix {{
                margin: 30px 0;
                background: white;
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                overflow-x: auto;
            }}
            
            .matrix-header {{
                display: grid;
                grid-template-columns: 140px repeat(5, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }}
            
            .header-cell {{
                background: linear-gradient(135deg, #495057 0%, #6c757d 100%);
                color: white;
                padding: 15px 10px;
                text-align: center;
                border-radius: 8px;
                font-weight: bold;
                font-size: 0.9em;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                min-height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .matrix-row {{
                display: grid;
                grid-template-columns: 140px repeat(5, 1fr);
                gap: 10px;
                margin-bottom: 12px;
            }}
            
            .row-header {{
                background: linear-gradient(135deg, #6c757d 0%, #868e96 100%);
                color: white;
                padding: 15px 10px;
                text-align: center;
                border-radius: 8px;
                font-weight: bold;
                font-size: 0.9em;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                min-height: 50px;
            }}
            
            .matrix-cell {{
                padding: 20px 12px;
                text-align: center;
                border-radius: 10px;
                font-weight: bold;
                color: white;
                font-size: 0.85em;
                transition: all 0.3s ease;
                min-height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                border: 2px solid rgba(255,255,255,0.2);
            }}
            
            .matrix-cell:hover {{
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 6px 20px rgba(0,0,0,0.25);
                border-color: rgba(255,255,255,0.4);
            }}
            
            .risk-score {{
                font-size: 1.4em;
                font-weight: bold;
                margin-bottom: 8px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            }}
            
            .risk-item {{
                background: rgba(255,255,255,0.95);
                color: #333;
                padding: 6px 8px;
                border-radius: 6px;
                font-size: 0.8em;
                margin: 3px 0;
                border: 1px solid rgba(0,0,0,0.1);
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                font-weight: 500;
                line-height: 1.3;
            }}
            
            .risk-item.empty {{
                background: rgba(255,255,255,0.2);
                color: rgba(255,255,255,0.8);
                border: 2px dashed rgba(255,255,255,0.4);
                font-weight: normal;
            }}
            
            .matrix-guide {{
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #dee2e6;
            }}
            
            .guide-items {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin: 15px 0;
            }}
            
            .guide-item {{
                display: flex;
                align-items: center;
                gap: 8px;
                background: white;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid #dee2e6;
            }}
            
            .guide-color {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
            }}
            
            .guide-color.risk-very-low {{ background-color: #28a745; }}
            .guide-color.risk-low {{ background-color: #6f42c1; }}
            .guide-color.risk-medium {{ background-color: #ffc107; }}
            .guide-color.risk-high {{ background-color: #fd7e14; }}
            .guide-color.risk-very-high {{ background-color: #dc3545; }}
            
            .matrix-explanation {{
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }}
            
            /* 모바일 반응형 디자인 */
            @media (max-width: 768px) {{
                .risk-matrix {{
                    padding: 15px;
                    margin: 20px 0;
                }}
                
                .matrix-header,
                .matrix-row {{
                    grid-template-columns: 120px repeat(5, 1fr);
                    gap: 6px;
                }}
                
                .header-cell,
                .row-header {{
                    padding: 10px 6px;
                    font-size: 0.75em;
                    min-height: 40px;
                }}
                
                .matrix-cell {{
                    padding: 15px 8px;
                    min-height: 80px;
                    font-size: 0.75em;
                }}
                
                .risk-score {{
                    font-size: 1.2em;
                }}
                
                .risk-item {{
                    font-size: 0.7em;
                    padding: 4px 6px;
                }}
                
                .guide-items {{
                    flex-direction: column;
                    gap: 10px;
                }}
            }}
            
            @media (max-width: 480px) {{
                .matrix-header,
                .matrix-row {{
                    grid-template-columns: 100px repeat(5, 1fr);
                    gap: 4px;
                }}
                
                .header-cell,
                .row-header {{
                    padding: 8px 4px;
                    font-size: 0.7em;
                    min-height: 35px;
                }}
                
                .matrix-cell {{
                    padding: 12px 6px;
                    min-height: 70px;
                    font-size: 0.7em;
                }}
                
                .risk-score {{
                    font-size: 1.1em;
                }}
                
                .risk-item {{
                    font-size: 0.65em;
                    padding: 3px 5px;
                }}
            }}
            
            .matrix-explanation p {{
                margin: 8px 0;
                font-size: 0.9em;
            }}
            
            .risk-item {{
                background: #f8f9fa;
                border-left: 4px solid #007bff;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                transition: all 0.3s ease;
            }}
            
            .risk-item:hover {{
                background: #e9ecef;
                transform: translateX(5px);
            }}
            
            /* 단계별 상세 스타일 */
            .step-details {{
                display: flex;
                gap: 30px;
                margin-top: 20px;
            }}
            
            .score-section {{
                flex: 0 0 200px;
                background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
                padding: 20px;
                border-radius: 10px;
                border: 2px solid #28a745;
            }}
            
            .score-value {{
                color: #155724;
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .assessment-value {{
                color: #856404;
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .action-guide {{
                flex: 1;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 10px;
                border: 2px solid #6c757d;
            }}
            
            .action-guide h5 {{
                color: #495057;
                margin: 20px 0 10px 0;
                font-size: 1.1em;
                border-bottom: 2px solid #dee2e6;
                padding-bottom: 5px;
            }}
            
            .action-guide ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            
            .action-guide li {{
                margin: 8px 0;
                line-height: 1.5;
            }}
            
            .action-guide strong {{
                color: #007bff;
            }}
            
            .overall-assessment {{
                background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                border: 2px solid #ffc107;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }}
            
            .improvement-roadmap {{
                margin-top: 25px;
            }}
            
            .roadmap-item {{
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            
            .roadmap-item h5 {{
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.1em;
                border-bottom: 2px solid #ffc107;
                padding-bottom: 8px;
            }}
            
            .roadmap-item ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            
            .roadmap-item li {{
                margin: 8px 0;
                line-height: 1.4;
            }}
            
            /* 새로운 갭분석 스타일 */
            .company-assessment {{
                background: #f8f9ff;
                border-left: 4px solid #4f46e5;
                padding: 15px;
                border-radius: 8px;
                font-style: italic;
                margin: 10px 0;
            }}
            
            .gap-list, .recommendation-list, .priority-list, .success-factors {{
                background: #fafbff;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }}
            
            .gap-item {{
                background: #fee2e2;
                border-left: 3px solid #ef4444;
                padding: 8px 12px;
                margin: 6px 0;
                border-radius: 5px;
                font-weight: 500;
            }}
            
            .recommendation-item {{
                background: #dcfce7;
                border-left: 3px solid #22c55e;
                padding: 8px 12px;
                margin: 6px 0;
                border-radius: 5px;
                font-weight: 500;
            }}
            
            .priority-item {{
                background: #fef3c7;
                border-left: 3px solid #f59e0b;
                padding: 8px 12px;
                margin: 6px 0;
                border-radius: 5px;
                font-weight: 500;
            }}
            
            .success-item {{
                background: #e0e7ff;
                border-left: 3px solid #6366f1;
                padding: 8px 12px;
                margin: 6px 0;
                border-radius: 5px;
                font-weight: 500;
            }}
            
            .roadmap-phases {{
                display: flex;
                flex-direction: column;
                gap: 15px;
                margin: 15px 0;
            }}
            
            .phase-item {{
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                border: 2px solid #cbd5e1;
                border-radius: 12px;
                padding: 20px;
                position: relative;
            }}
            
            .phase-item.phase1 {{
                border-color: #3b82f6;
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            }}
            
            .phase-item.phase2 {{
                border-color: #10b981;
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            }}
            
            .phase-item.phase3 {{
                border-color: #f59e0b;
                background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
            }}
            
            .phase-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            
            .phase-badge {{
                background: #4f46e5;
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
            }}
            
            .phase1 .phase-badge {{
                background: #3b82f6;
            }}
            
            .phase2 .phase-badge {{
                background: #10b981;
            }}
            
            .phase3 .phase-badge {{
                background: #f59e0b;
            }}
            
            .phase-timeline {{
                background: rgba(255, 255, 255, 0.8);
                padding: 4px 10px;
                border-radius: 15px;
                font-size: 0.8em;
                color: #374151;
                font-weight: 500;
            }}
            
            .phase-content {{
                color: #374151;
                line-height: 1.5;
                font-size: 0.95em;
            }}
            
            .cost-priority-section {{
                background: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
            }}
            
            .cost-estimate {{
                margin-bottom: 15px;
                padding: 10px;
                background: white;
                border-radius: 8px;
            }}
            
            .cost-range {{
                color: #0891b2;
                font-weight: bold;
                font-size: 1.1em;
            }}
            
            .priority-areas {{
                padding: 10px;
                background: white;
                border-radius: 8px;
            }}
            
            /* 마크다운 변환 스타일 */
            .md-title {{
                color: #1f2937;
                font-size: 1.6em;
                font-weight: bold;
                margin: 25px 0 15px 0;
                border-bottom: 3px solid #3b82f6;
                padding-bottom: 10px;
            }}
            
            .md-subtitle {{
                color: #374151;
                font-size: 1.3em;
                font-weight: bold;
                margin: 20px 0 12px 0;
                border-left: 4px solid #10b981;
                padding-left: 15px;
                background: #f0fdf4;
                padding: 8px 15px;
                border-radius: 5px;
            }}
            
            .md-subheading {{
                color: #4b5563;
                font-size: 1.1em;
                font-weight: 600;
                margin: 15px 0 10px 0;
            }}
            
            .md-paragraph {{
                line-height: 1.6;
                margin: 10px 0;
                color: #374151;
            }}
            
            .md-list {{
                margin: 15px 0;
                padding-left: 20px;
            }}
            
            .md-list-item {{
                margin: 8px 0;
                line-height: 1.5;
                color: #374151;
            }}
            
            .md-list-item strong {{
                color: #1f2937;
                font-weight: 600;
            }}
            
            .scenario-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #dee2e6;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                transition: all 0.3s ease;
            }}
            
            .scenario-card:hover {{
                border-color: #007bff;
                box-shadow: 0 4px 15px rgba(0,123,255,0.2);
            }}
            
            .scenario-title {{
                font-size: 1.3em;
                font-weight: bold;
                color: #1e3c72;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #dee2e6;
            }}
            
            .risk-level-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
                margin: 10px 5px;
                color: white;
            }}
            
            .risk-very-high {{ background-color: #dc3545; }}
            .risk-high {{ background-color: #fd7e14; }}
            .risk-medium {{ background-color: #ffc107; color: #333; }}
            .risk-low {{ background-color: #6f42c1; }}
            .risk-very-low {{ background-color: #28a745; }}
            
            .relevance-high {{
                background-color: #28a745;
                color: white;
                padding: 4px 8px;
                border-radius: 10px;
                font-size: 0.8em;
                font-weight: bold;
            }}
            
            .relevance-medium {{
                background-color: #ffc107;
                color: #212529;
                padding: 4px 8px;
                border-radius: 10px;
                font-size: 0.8em;
                font-weight: bold;
            }}
            
            .data-methodology {{
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border: 2px solid #2196f3;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
            }}
            
            .ai-insight {{
                background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
                border: 2px solid #9c27b0;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
            }}
            
            .personalized-report {{
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                border: 2px solid #ff9800;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
            }}
            
            .footer {{
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                text-align: center;
                padding: 40px 30px;
                margin-top: 40px;
            }}
            
            .footer p {{
                margin: 10px 0;
                opacity: 0.9;
            }}
            
            .toc {{
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 15px;
                padding: 25px;
                margin: 25px 0;
            }}
            
            .toc h3 {{
                color: #1e3c72;
                margin-bottom: 15px;
            }}
            
            .toc ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .toc li {{
                padding: 8px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            
            .toc a {{
                color: #007bff;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .toc a:hover {{
                color: #0056b3;
                text-decoration: underline;
            }}
            
            @media (max-width: 768px) {{
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 20px 15px;
                }}
                
                .section {{
                    padding: 20px;
                }}
                
                .risk-matrix {{
                    grid-template-columns: repeat(3, 1fr);
                }}
                
                /* 리스크 매트릭스 시각화 스타일 */
                .risk-matrix-visual {{
                    margin: 30px 0;
                }}
                
                .matrix-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{company_name} 통합 종합 분석보고서</h1>
                <div class="subtitle">2025년 8월 {company_name} 리스크 관리수준 종합분석</div>
                <div class="badge-container">
                    
                    <span class="badge badge-ai">🤖 GPT-4o-mini AI 분석</span>
                    <span class="badge badge-integrated">📊 통합 종합 분석</span>
                </div>
            </div>
            
            <div class="content">
                <!-- 목차 -->
                <div class="section">
                    <h2>📋 목차</h2>
                    <div class="toc">
                        <h3>보고서 구성</h3>
                        <ul>
                            <li><a href="#executive-summary">1. 실행 요약</a></li>
                            <li><a href="#data-methodology">2. 데이터 종합 분석 방법론</a></li>
                            <li><a href="#iso-readiness">3. ISO 인증 준비도 평가 및 권고</a></li>
                            <li><a href="#identified-risks">4. 식별된 리스크 분석</a></li>
                            <li><a href="#ai-contextual">5. AI 맥락적 리스크 분석</a></li>
                            <li><a href="#ai-scenarios">6. AI 생성 리스크 시나리오</a></li>
                            <li><a href="#personalized-reports">7. AI 맞춤형 분석 보고서</a></li>
                            <li><a href="#monitoring">8. 모니터링 및 후속조치</a></li>
                            <li><a href="#business-outlook">9. 비즈니스 전망</a></li>
                        </ul>
                    </div>
                </div>
                
                <!-- 실행 요약 -->
                <div class="section" id="executive-summary">
                    <h2>🚀 실행 요약</h2>
                    <div class="risk-summary">
                        <h3>종합 리스크 평가</h3>
                        <div class="risk-score">{integrated_risk_score:.2f}</div>
                        <div class="risk-level">리스크 레벨: {risk_level}</div>
                        <p>본 보고서는 {company_name}의 리스크 관리 현황을 AI 기반 지능형 분석을 통해 종합적으로 평가한 결과입니다.</p>
                    </div>
                    
                    <h3>📊 핵심 분석 결과</h3>
                    <ul>
                        <li><strong>통합 리스크 점수:</strong> {integrated_risk_score:.2f}</li>
                        <li><strong>FinBERT 기반 점수:</strong> {risk_score:.2f}</li>
                        
                        <li><strong>AI 분석 신뢰도:</strong> ChatGPT GPT-4o-mini + 기존 분석 시스템</li>
                        <li><strong>주요 리스크 요소:</strong> 리콜|recall, 소송|lawsuit|litigation|class action, 해킹|유출|breach|hack|data leak|ransom, 제재|sanction|embargo, 회계\\s?부정|fraud|accounting scandal</li>
                        <li><strong>분석 데이터 소스:</strong> 뉴스, 소셜미디어, 공시, FinBERT, AI 분석</li>
                    </ul>
                    
                    <h3>🎯 데이터 일관성 설명</h3>
                    <div class="consistency-explanation">
                        <p><strong>통합 리스크 점수 계산 방식:</strong></p>
                        <ul>
                            <li><strong>FinBERT 감성분석:</strong> 뉴스 및 텍스트 데이터의 감성 분석 결과 (40% 가중치)</li>
                            
                            <li><strong>최종 점수:</strong> 두 점수의 가중 평균으로 일관성 있는 리스크 평가</li>
                        </ul>
                    </div>
                </div>
                
                <!-- ISO 인증 준비도 평가 및 권고 -->
                <div class="section" id="iso-readiness">
                    <h2>🛡️ ISO 인증 준비도 평가 및 권고</h2>
                    <div class="overall-assessment">
                        <p><strong>전체 준비도:</strong> {report.get('iso_assessment', {}).get('overall_score', '-')}/100 · <strong>상태:</strong> {report.get('iso_assessment', {}).get('overall_status', '-')}</p>
                        <p><strong>권고 표준:</strong> {report.get('iso_recommendation', {}).get('standard', '-')}</p>
                    </div>
                    <div class="step-details">
                        <div class="score-section">
                            <p><strong>ISO 9001</strong></p>
                            <p class="score-value">{report.get('iso_assessment', {}).get('standards', {}).get('9001', {}).get('readiness_score', '-')} / 100</p>
                            <p class="assessment-value">{report.get('iso_assessment', {}).get('standards', {}).get('9001', {}).get('status', '-')}</p>
                        </div>
                        <div class="score-section">
                            <p><strong>ISO 14001</strong></p>
                            <p class="score-value">{report.get('iso_assessment', {}).get('standards', {}).get('14001', {}).get('readiness_score', '-')} / 100</p>
                            <p class="assessment-value">{report.get('iso_assessment', {}).get('standards', {}).get('14001', {}).get('status', '-')}</p>
                        </div>
                        <div class="score-section">
                            <p><strong>ISO 45001</strong></p>
                            <p class="score-value">{report.get('iso_assessment', {}).get('standards', {}).get('45001', {}).get('readiness_score', '-')} / 100</p>
                            <p class="assessment-value">{report.get('iso_assessment', {}).get('standards', {}).get('45001', {}).get('status', '-')}</p>
                        </div>
                    </div>
                    <div class="improvement-roadmap">
                        <!-- 회사별 맞춤 평가 -->
                        <div class="roadmap-item">
                            <h5>🏢 맞춤형 현황 분석</h5>
                            <div class="company-assessment">
                                <p>{report.get('iso_recommendation', {}).get('company_specific_assessment', '')}</p>
                            </div>
                        </div>
                        
                        <!-- 핵심 갭 분석 -->
                        <div class="roadmap-item">
                            <h5>🎯 핵심 갭 분석</h5>
                            <ul class="gap-list">
                                {''.join([f'<li class="gap-item">🔴 {gap}</li>' for gap in report.get('iso_recommendation', {}).get('key_gaps', [])])}
                            </ul>
                        </div>
                        
                        <!-- 맞춤형 권고사항 -->
                        <div class="roadmap-item">
                            <h5>✅ 맞춤형 개선 방안</h5>
                            <ul class="recommendation-list">
                                {''.join([f'<li class="recommendation-item">✨ {rec}</li>' for rec in report.get('iso_recommendation', {}).get('customized_recommendations', [])])}
                            </ul>
                        </div>
                        
                        <!-- 단계별 구현 로드맵 -->
                        <div class="roadmap-item">
                            <h5>🚀 단계별 구현 로드맵</h5>
                            <div class="roadmap-phases">
                                <div class="phase-item phase1">
                                    <div class="phase-header">
                                        <span class="phase-badge">1단계</span>
                                        <span class="phase-timeline">초기 단계</span>
                                    </div>
                                    <p class="phase-content">{report.get('iso_recommendation', {}).get('implementation_roadmap', {}).get('phase1', '')}</p>
                                </div>
                                <div class="phase-item phase2">
                                    <div class="phase-header">
                                        <span class="phase-badge">2단계</span>
                                        <span class="phase-timeline">시스템 구축</span>
                                    </div>
                                    <p class="phase-content">{report.get('iso_recommendation', {}).get('implementation_roadmap', {}).get('phase2', '')}</p>
                                </div>
                                <div class="phase-item phase3">
                                    <div class="phase-header">
                                        <span class="phase-badge">3단계</span>
                                        <span class="phase-timeline">운영 정착</span>
                                    </div>
                                    <p class="phase-content">{report.get('iso_recommendation', {}).get('implementation_roadmap', {}).get('phase3', '')}</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 비용 및 우선순위 -->
                        <div class="roadmap-item">
                            <h5>💰 예상 비용 및 우선순위</h5>
                            <div class="cost-priority-section">
                                <div class="cost-estimate">
                                    <strong>📊 예상 비용 범위:</strong> 
                                    <span class="cost-range">{report.get('iso_recommendation', {}).get('estimated_cost_range', '')}</span>
                                </div>
                                <div class="priority-areas">
                                    <strong>⭐ 우선순위 영역:</strong>
                                    <ul class="priority-list">
                                        {''.join([f'<li class="priority-item">🎯 {area}</li>' for area in report.get('iso_recommendation', {}).get('priority_areas', [])])}
                                    </ul>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 성공 요인 -->
                        <div class="roadmap-item">
                            <h5>🎯 성공 요인</h5>
                            <ul class="success-factors">
                                {''.join([f'<li class="success-item">🌟 {factor}</li>' for factor in report.get('iso_recommendation', {}).get('success_factors', [])])}
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- 데이터 종합 분석 방법론 -->
                <div class="section" id="data-methodology">
                    <h2>🔬 데이터 종합 분석 방법론</h2>
                    <div class="data-methodology">
                        <h3>📈 다중 데이터 소스 통합 분석</h3>
                        <p>본 보고서는 다음과 같은 다양한 데이터 소스를 종합적으로 분석하여 리스크를 평가합니다:</p>
                        
                        <h4>1. 뉴스 및 미디어 데이터</h4>
                        <ul>
                            <li><strong>뉴스 기사:</strong> 최신 {len(news)}건의 뉴스 데이터 분석</li>
                            <li><strong>감성 분석:</strong> FinBERT 모델을 활용한 뉴스 톤 분석</li>
                            <li><strong>키워드 추출:</strong> 리스크 관련 핵심 키워드 식별</li>
                        </ul>
                        
                        <h4>2. 소셜미디어 및 시장 반응</h4>
                        <ul>
                            <li><strong>소셜미디어:</strong> Reddit, Stocktwits 등 {len(social_media)}건의 데이터</li>
                            <li><strong>투자자 심리:</strong> 실시간 시장 반응 및 감정 분석</li>
                            <li><strong>트렌드 파악:</strong> 시장 관심도 및 논의 주제 분석</li>
                        </ul>
                        
                        <h4>3. 공시 및 규제 데이터</h4>
                        <ul>
                            <li><strong>기업 공시:</strong> 최신 {len(filings)}건의 공시 자료 분석</li>
                            <li><strong>규제 준수:</strong> 관련 법규 및 규제 요구사항 검토</li>
                            <li><strong>리스크 공개:</strong> 기업이 공개한 리스크 정보 분석</li>
                        </ul>
                        
                        <h4>4. AI 기반 지능형 분석</h4>
                        <ul>
                            <li><strong>맥락적 해석:</strong> ChatGPT GPT-4o-mini를 활용한 데이터 맥락 분석</li>
                            <li><strong>시나리오 생성:</strong> 미래 리스크 시나리오 예측 및 분석</li>
                            <li><strong>맞춤형 인사이트:</strong> 사용자 프로필별 맞춤형 분석 결과</li>
                        </ul>
                        
                        
                        <ul>
                            
                            <li><strong>체계적 평가:</strong> 구조화된 리스크 식별, 분석, 평가 프로세스</li>
                            <li><strong>정량적 측정:</strong> 리스크 매트릭스를 활용한 객관적 평가</li>
                        </ul>
                    </div>
                </div>
                
                
                
                <!-- 식별된 리스크 분석 -->
                <div class="section" id="identified-risks">
                    <h2>🔍 식별된 리스크 분석</h2>
                    
                                             <h3>📊 FinBERT 감성 분석 결과</h3>
                         <div class="risk-item">
                             <p><strong>긍정적 뉴스:</strong> {finbert_data.get('pos', '데이터 없음')}</p>
                             <p><strong>부정적 뉴스:</strong> {finbert_data.get('neg', '데이터 없음')}</p>
                             <p><strong>중립적 뉴스:</strong> {finbert_data.get('neu', '데이터 없음')}</p>
                         </div>
                    
                    <h3>🔑 키워드 기반 리스크 식별</h3>
                    <div class="risk-item">
                        <p><strong>총 키워드 히트:</strong> {keyword_hits_total}건</p>
                        <p><strong>주요 리스크 키워드:</strong></p>
                        {format_list(list(keyword_hits.keys())[:10]) if keyword_hits and keyword_hits != {'리스크 키워드': '데이터 없음'} else '<p>데이터 없음</p>'}
                    </div>
                </div>
                

                
                <!-- AI 맥락적 리스크 분석 -->
                <div class="section" id="ai-contextual">
                    <h2>🔍 AI 맥락적 리스크 분석</h2>
                    
                    <h3>🎯 AI 맥락적 인사이트</h3>
                    <div class="ai-contextual-analysis">
                        <h4>🔗 데이터 간 상관관계</h4>
                        <div class="ai-insight">
                            <p><strong>뉴스 감성과 주가 연관성:</strong> FinBERT 분석 결과와 시장 반응 간의 상관관계를 통해 리스크 전파 경로를 파악할 수 있습니다.</p>
                            <p><strong>소셜미디어 트렌드:</strong> 투자자 심리 변화가 시장 변동성에 미치는 영향을 실시간으로 모니터링합니다.</p>
                        </div>
                    </div>
                    
                    <h3>🎯 숨겨진 리스크 요소</h3>
                    <div class="ai-insight">{format_list(ai_contextual_analysis.get('hidden_risks', ['AI 분석을 위해 추가 데이터가 필요합니다.']))}</div>
                    
                    <h3>📊 시장 맥락 및 트렌드</h3>
                    <div class="ai-insight"><p>{ai_contextual_analysis.get('market_context', '시장 맥락 분석을 위해 추가 데이터가 필요합니다.')}</p></div>
                    
                    <h3>🏆 경쟁사 동향 분석</h3>
                    <div class="ai-insight"><p>{ai_contextual_analysis.get('competitive_analysis', '경쟁사 분석을 위해 추가 데이터가 필요합니다.')}</p></div>
                    
                    <h3>⚖️ 규제 환경 변화</h3>
                    <div class="ai-insight"><p>{ai_contextual_analysis.get('regulatory_implications', '규제 환경 분석을 위해 추가 데이터가 필요합니다.')}</p></div>
                    
                    <h3>💹 투자자 심리 및 시장 신뢰도</h3>
                    <div class="ai-insight"><p>{ai_contextual_analysis.get('investor_sentiment', '투자자 심리 분석을 위해 추가 데이터가 필요합니다.')}</p></div>
                    
                    <h3>💡 AI 권장사항</h3>
                    <div class="ai-insight">{format_list(ai_contextual_analysis.get('recommendations', ['구체적인 권장사항을 위해 추가 분석이 필요합니다.']))}</div>
                </div>
                
                <!-- AI 생성 리스크 시나리오 -->
                <div class="section" id="ai-scenarios">
                    <h2>🔮 AI 생성 리스크 시나리오</h2>
                    <p>ChatGPT AI가 현재 데이터를 바탕으로 향후 6개월 내 발생 가능한 리스크 시나리오를 생성했습니다.</p>
                    {format_risk_scenarios(ai_risk_scenarios)}
                </div>
                
                <!-- AI 맞춤형 분석 보고서 -->
                <div class="section" id="personalized-reports">
                    <h2>📋 AI 맞춤형 분석 보고서</h2>
                    
                    <h3>👔 경영진용 맞춤 보고서</h3>
                    <div class="personalized-report">{markdown_to_html(ai_personalized_reports.get('executive', '경영진용 보고서 생성 중 오류가 발생했습니다.'))}</div>
                    
                    <h3>💰 투자자용 맞춤 보고서</h3>
                    <div class="personalized-report">{markdown_to_html(ai_personalized_reports.get('investor', '투자자용 보고서 생성 중 오류가 발생했습니다.'))}</div>
                </div>
                
                <!-- 모니터링 및 후속조치 -->
                <div class="section" id="monitoring">
                    <h2>📊 모니터링 및 후속조치</h2>
                    
                    <h3>🔍 지속적 모니터링</h3>
                    <ul>
                        <li><strong>정기 리뷰:</strong> 분기별 리스크 평가 및 업데이트</li>
                        <li><strong>KPI 추적:</strong> 리스크 관리 성과 지표 모니터링</li>
                        <li><strong>경고 시스템:</strong> 리스크 임계값 초과 시 자동 알림</li>
                    </ul>
                    
                    <h3>📈 개선 계획</h3>
                    <ul>
                        <li><strong>프로세스 개선:</strong> 리스크 관리 워크플로우 최적화</li>
                        <li><strong>기술 업그레이드:</strong> AI 분석 시스템 지속적 개선</li>
                        <li><strong>훈련 및 교육:</strong> 직원 리스크 관리 역량 강화</li>
                    </ul>
                </div>
                
                <!-- 비즈니스 전망 -->
                <div class="section" id="business-outlook">
                    <h2>🔮 비즈니스 전망</h2>
                    
                    <h3>📊 단기 전망 (3-6개월)</h3>
                    <div class="risk-item">
                        <p>현재 식별된 리스크 요소들의 단기적 영향과 대응 효과를 모니터링하여 비즈니스 안정성을 확보합니다.</p>
                    </div>
                    
                    <h3>📈 중기 전망 (6-12개월)</h3>
                    <div class="risk-item">
                        <p>AI 시나리오 분석을 바탕으로 한 예방적 리스크 관리와 새로운 기회 요인 발굴을 통해 지속적 성장을 추구합니다.</p>
                    </div>
                    
                    <h3>🚀 장기 전망 (1년 이상)</h3>
                    <div class="risk-item">
                        
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>본 보고서는 OpenAI GPT-4o-mini AI 모델을 활용하여 생성되었습니다.</p>
                <p>© 2025 ISOMatch 통합 종합 분석 시스템</p>
            </div>
        </div>
    </body>
    </html>"""
    
    return html

if __name__ == "__main__":
    main()
