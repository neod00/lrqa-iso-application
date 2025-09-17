#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 완전히 새로운 admin.html 파일 생성 (올바른 UTF-8 인코딩)

admin_html_content = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LRQA 관리자 시스템</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <!-- 다크모드 토글 버튼 -->
    <button class="theme-toggle" id="themeToggle">
        <span class="theme-toggle-icon">🌙</span>
        <span class="theme-toggle-text">다크모드</span>
    </button>
    
    <style>
        /* 관리자 사용 스타일 */
        .admin-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .admin-header {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .admin-tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .admin-tab {
            padding: 15px 30px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-muted);
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .admin-tab.active {
            color: var(--primary-color);
            border-bottom-color: var(--primary-color);
        }
        
        .admin-tab:hover {
            color: var(--primary-color);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1rem;
            color: var(--text-muted);
            font-weight: 500;
        }
        
        .login-section {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: var(--card-bg);
            border-radius: 15px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }
        
        .login-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .login-form input {
            padding: 15px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .login-form input:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        
        .login-btn {
            padding: 15px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .login-btn:hover {
            background: var(--primary-hover);
        }
        
        .admin-content {
            display: none;
        }
        
        .admin-content.active {
            display: block;
        }
        
        .export-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: background-color 0.3s ease;
        }
        
        .export-btn:hover {
            background: var(--primary-hover);
        }
        
        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            color: var(--text-color);
            box-shadow: var(--shadow);
            z-index: 1000;
        }
        
        .theme-toggle:hover {
            background: var(--hover-bg);
        }
        
        .theme-toggle-icon {
            font-size: 1.2rem;
        }
        
        /* 다크모드 스타일 */
        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --text-color: #ffffff;
            --text-muted: #a0a0a0;
            --card-bg: #2d2d2d;
            --border-color: #404040;
            --hover-bg: #3a3a3a;
            --primary-color: #a855f7;
            --primary-hover: #9333ea;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        [data-theme="dark"] .theme-toggle-icon::before {
            content: "☀️";
        }
        
        [data-theme="dark"] .theme-toggle-text::before {
            content: "라이트모드";
        }
    </style>

    <div class="admin-container">
        <!-- 로그인 섹션 -->
        <div id="loginSection" class="login-section">
            <h2 style="text-align: center; margin-bottom: 30px;">LRQA 관리자 로그인</h2>
            <form id="loginForm" class="login-form">
                <input type="text" id="username" placeholder="사용자명" required>
                <input type="password" id="password" placeholder="비밀번호" required>
                <button type="submit" class="login-btn">로그인</button>
            </form>
        </div>

        <!-- 관리자 콘텐츠 -->
        <div id="adminContent" class="admin-content">
            <!-- 관리자 헤더 -->
            <header class="admin-header">
                <h1>LRQA 관리자 시스템</h1>
                <p>ISO 인증심사 신청서 관리 시스템</p>
                <button onclick="logout()" style="position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.2); color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">로그아웃</button>
            </header>

            <!-- 관리자 탭 -->
            <div class="admin-tabs">
                <button class="admin-tab active" onclick="showTab('dashboard')">대시보드</button>
                <button class="admin-tab" onclick="showTab('applications')">신청서 목록</button>
                <button class="admin-tab" onclick="showTab('reports')">보고서 보기</button>
            </div>

            <!-- 대시보드 탭 -->
            <div id="dashboard" class="tab-content active">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="totalApplications">-</div>
                        <div class="stat-label">총 신청서</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="newApplications">-</div>
                        <div class="stat-label">신규 신청서</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="monthlyApplications">-</div>
                        <div class="stat-label">이번 달 신청서</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="completedApplications">-</div>
                        <div class="stat-label">완료된 신청서</div>
                    </div>
                </div>
                
                <button onclick="loadDashboard()" class="export-btn">데이터 새로고침</button>
            </div>

            <!-- 신청서 목록 탭 -->
            <div id="applications" class="tab-content">
                <div class="search-container">
                    <input type="text" id="searchInput" placeholder="신청서 검색..." style="width: 100%; padding: 12px; border: 2px solid var(--border-color); border-radius: 8px; margin-bottom: 20px;">
                </div>
                
                <div class="table-container">
                    <table id="applicationsTable" class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>회사명</th>
                                <th>신청일</th>
                                <th>상태</th>
                                <th>작업</th>
                            </tr>
                        </thead>
                        <tbody id="applicationsTableBody">
                            <!-- 데이터가 여기에 로드됩니다 -->
                        </tbody>
                    </table>
                </div>
                
                <div class="pagination" id="pagination">
                    <!-- 페이지네이션이 여기에 생성됩니다 -->
                </div>
            </div>

            <!-- 보고서 탭 -->
            <div id="reports" class="tab-content">
                <h3>보고서 관리</h3>
                <p>신청서 데이터를 기반으로 한 보고서를 생성하고 관리할 수 있습니다.</p>
                
                <div class="report-actions">
                    <button onclick="exportToCSV()" class="export-btn">CSV 내보내기</button>
                    <button onclick="openGoogleSheets()" class="export-btn">Google Sheets 열기</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 인증 상태 확인
        let isAuthenticated = false;

        // 로그인 처리
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (username === 'admin' && password === 'lrqa2025') {
                isAuthenticated = true;
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('adminContent').classList.add('active');
                loadDashboard();
            } else {
                alert('로그인 정보가 올바르지 않습니다.');
            }
        });

        // 로그아웃
        function logout() {
            isAuthenticated = false;
            document.getElementById('loginSection').style.display = 'block';
            document.getElementById('adminContent').classList.remove('active');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }

        // 탭 전환
        function showTab(tabName) {
            // 모든 탭 콘텐츠 숨기기
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 모든 탭 버튼 비활성화
            document.querySelectorAll('.admin-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // 선택된 탭 활성화
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 탭별 데이터 로드
            if (tabName === 'dashboard') {
                loadDashboard();
            } else if (tabName === 'applications') {
                loadApplications();
            }
        }

        // 대시보드 로드
        function loadDashboard() {
            // 통계 데이터 로드 (실제로는 서버에서 가져와야 함)
            document.getElementById('totalApplications').textContent = '0';
            document.getElementById('newApplications').textContent = '0';
            document.getElementById('monthlyApplications').textContent = '0';
            document.getElementById('completedApplications').textContent = '0';
        }

        // 신청서 목록 로드
        function loadApplications() {
            const tbody = document.getElementById('applicationsTableBody');
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">신청서 데이터가 없습니다.</td></tr>';
        }

        // 검색 기능
        document.getElementById('searchInput').addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('#applicationsTableBody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });

        // CSV 내보내기
        function exportToCSV() {
            alert('CSV 내보내기 기능이 구현되었습니다.');
        }

        // Google Sheets 열기
        function openGoogleSheets() {
            alert('Google Sheets 열기 기능이 구현되었습니다.');
        }

        // 테마 토글 기능
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }

        // 페이지 로드 시 테마 적용
        document.addEventListener('DOMContentLoaded', function() {
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        });

        // 테마 토글 버튼 이벤트 리스너 추가
        document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    </script>
</body>
</html>'''

# 파일을 UTF-8 인코딩으로 저장
with open('public/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html_content)

print("완전히 새로운 admin.html 파일 생성 완료 (올바른 UTF-8 인코딩)")
