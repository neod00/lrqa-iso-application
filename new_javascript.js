    <script>
        // 인증 상태 확인
        let isAuthenticated = false;
        
        // 로그인 처리
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // 간단한 인증 (실제 환경에서는 보안 방법 사용)
            if (username === 'admin' && password === 'lrqa2025') {
                isAuthenticated = true;
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('adminContent').classList.add('authenticated');
                loadDashboard();
            } else {
                alert('로그인 정보가 올바르지 않습니다.');
            }
        });

        // 로그아웃
        function logout() {
            isAuthenticated = false;
            document.getElementById('loginSection').style.display = 'block';
            document.getElementById('adminContent').classList.remove('authenticated');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }

        // 탭 전환
        function showTab(tabName) {
            // 모든 탭 비활성화
            const tabs = document.querySelectorAll('.admin-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 선택된 탭 활성화
            document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
            
            // 탭 내용 표시
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.style.display = 'none');
            document.getElementById(tabName).style.display = 'block';
            
            // 탭별 데이터 로드
            if (tabName === 'applications') {
                loadApplications();
            }
        }

        // 대시보드 로드
        async function loadDashboard() {
            if (!isAuthenticated) return;
            
            try {
                // 실제 환경에서는 API 호출
                // const response = await fetch('/.netlify/functions/get-applications');
                // const result = await response.json();
                
                // 임시 데이터로 대시보드 업데이트
                updateDashboardStats({
                    total: 25,
                    pending: 8,
                    completed: 17,
                    thisMonth: 5
                });
                
            } catch (error) {
                console.error('대시보드 로드 오류:', error);
            }
        }

        // 대시보드 통계 업데이트
        function updateDashboardStats(stats) {
            document.querySelector('.stat-card:nth-child(1) h3').textContent = stats.total;
            document.querySelector('.stat-card:nth-child(2) h3').textContent = stats.pending;
            document.querySelector('.stat-card:nth-child(3) h3').textContent = stats.completed;
            document.querySelector('.stat-card:nth-child(4) h3').textContent = stats.thisMonth;
        }

        // 신청서 목록 로드
        async function loadApplications() {
            if (!isAuthenticated) return;
            
            try {
                // 실제 환경에서는 API 호출
                // const response = await fetch('/.netlify/functions/get-applications');
                // const result = await response.json();
                
                // 임시 데이터로 테이블 업데이트
                const applications = [
                    {
                        id: 'APP001',
                        company: '김달주식회사',
                        contact: '김달수',
                        phone: '02-1234-5678',
                        date: '2025-01-14',
                        status: '대기 중'
                    },
                    {
                        id: 'APP002',
                        company: 'ABC제조업체',
                        contact: '이영희',
                        phone: '02-2345-6789',
                        date: '2025-01-13',
                        status: '처리 중'
                    },
                    {
                        id: 'APP003',
                        company: 'DEF환경기업',
                        contact: '박민수',
                        phone: '02-3456-7890',
                        date: '2025-01-12',
                        status: '완료'
                    }
                ];
                
                displayApplications(applications);
                
            } catch (error) {
                console.error('신청서 목록 로드 오류:', error);
                showMessage('신청서 목록을 불러오는 중 오류가 발생했습니다.', 'error');
            }
        }

        // 신청서 목록 표시
        function displayApplications(applications) {
            const tbody = document.getElementById('applicationsTableBody');
            if (!tbody) return;
            
            tbody.innerHTML = applications.map(app => `
                <tr>
                    <td>${app.id}</td>
                    <td>${app.company}</td>
                    <td>${app.contact}</td>
                    <td>${app.phone}</td>
                    <td>${app.date}</td>
                    <td><span class="status ${getStatusClass(app.status)}">${app.status}</span></td>
                    <td>
                        <button onclick="generateQuotation('${app.id}')" class="btn btn-primary">견적서</button>
                        <button onclick="viewApplication('${app.id}')" class="btn btn-secondary">보기</button>
                        <button onclick="editApplication('${app.id}')" class="btn btn-warning">수정</button>
                        <button onclick="deleteApplication('${app.id}')" class="btn btn-danger">삭제</button>
                    </td>
                </tr>
            `).join('');
        }

        // 상태 클래스 반환
        function getStatusClass(status) {
            switch(status) {
                case '신규': return 'status-new';
                case '진행중': return 'status-progress';
                case '완료': return 'status-completed';
                default: return 'status-new';
            }
        }

        // 견적서 생성
        function generateQuotation(appId) {
            alert(`견적서 생성: ${appId}\n\n이 기능은 견적서 생성 시스템과 연동됩니다.`);
        }

        // 신청서 보기
        function viewApplication(appId) {
            alert(`신청서 보기: ${appId}\n\n상세 정보를 표시합니다.`);
        }

        // 신청서 수정
        function editApplication(appId) {
            alert(`신청서 수정: ${appId}\n\n수정 폼을 표시합니다.`);
        }

        // 신청서 삭제
        function deleteApplication(appId) {
            if (confirm(`신청서 ${appId}를 삭제하시겠습니까?`)) {
                alert(`신청서 ${appId}가 삭제되었습니다.`);
                loadApplications(); // 목록 새로고침
            }
        }

        // 검색 실행
        function performSearch() {
            const searchTerm = document.getElementById('searchInput').value.trim().toLowerCase();
            // 검색 로직 구현
            console.log('검색어:', searchTerm);
        }

        // 검색 초기화
        function clearSearch() {
            document.getElementById('searchInput').value = '';
            loadApplications(); // 전체 목록 다시 로드
        }

        // 메시지 표시
        function showMessage(message, type) {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${type}`;
            messageElement.textContent = message;
            messageElement.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                animation: slideIn 0.3s ease;
            `;
            
            if (type === 'success') {
                messageElement.style.backgroundColor = '#28a745';
            } else if (type === 'error') {
                messageElement.style.backgroundColor = '#dc3545';
            } else if (type === 'info') {
                messageElement.style.backgroundColor = '#17a2b8';
            }
            
            document.body.appendChild(messageElement);
            
            setTimeout(() => {
                messageElement.remove();
            }, 3000);
        }

        // 페이지 로드 시 초기화
        window.addEventListener('load', function() {
            document.getElementById('loginSection').style.display = 'block';
            document.getElementById('adminContent').classList.remove('authenticated');
        });

        // Enter 키로 검색 실행
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        performSearch();
                    }
                });
            }
        });
    </script>
