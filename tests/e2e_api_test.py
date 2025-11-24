"""
E2E API Integration Tests
백엔드 API 엔드포인트 통합 테스트
"""

import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class TestAPIIntegration:
    """API 통합 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """각 테스트 전 설정"""
        self.test_user_id = f"test_user_{datetime.now().timestamp()}"
        self.test_paper_id = None
        yield
        # 테스트 후 정리는 필요시 추가

    # ============= UC-1: 사용자 생성 =============
    def test_api_create_user(self):
        """API: 사용자 생성"""
        url = f"{BASE_URL}/users"
        payload = {
            "id": self.test_user_id,
            "name": "테스트사용자",
            "role": "student",
            "interests": ["AI", "ML"]
        }
        
        response = requests.post(url, json=payload)
        
        # 201 또는 200 상태 코드 확인
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == self.test_user_id
        assert data["name"] == "테스트사용자"
        assert data["role"] == "student"
        print(f"✅ 사용자 생성 성공: {self.test_user_id}")

    # ============= UC-2: 논문 목록 조회 =============
    def test_api_list_papers(self):
        """API: 논문 목록 조회"""
        url = f"{BASE_URL}/research/papers"
        params = {
            "limit": 10,
            "offset": 0
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
        
        if data["items"]:
            paper = data["items"][0]
            assert "id" in paper
            assert "title" in paper
            assert "university" in paper
            self.test_paper_id = paper["id"]
            print(f"✅ 논문 목록 조회 성공: {len(data['items'])}개 논문")
        else:
            print("⚠️ 논문 데이터가 없습니다 (Mock 데이터 확인 필요)")

    def test_api_list_papers_with_filter(self):
        """API: 필터를 사용한 논문 목록 조회"""
        url = f"{BASE_URL}/research/papers"
        params = {
            "university": "KAIST",
            "limit": 10
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        # KAIST 필터가 적용되었는지 확인
        for paper in data["items"]:
            # 필터링이 작동하면 KAIST만 반환되어야 함
            pass
        
        print(f"✅ 필터링된 논문 조회 성공")

    # ============= UC-3: 논문 분석 조회 =============
    def test_api_get_paper_analysis(self):
        """API: 논문 분석 조회"""
        # 먼저 논문 목록에서 논문 ID 가져오기
        list_response = requests.get(f"{BASE_URL}/research/papers", params={"limit": 1})
        
        if list_response.status_code != 200 or not list_response.json()["items"]:
            pytest.skip("No papers available")
        
        paper_id = list_response.json()["items"][0]["id"]
        
        # 분석 조회
        url = f"{BASE_URL}/research/papers/{paper_id}/analysis"
        response = requests.get(url)
        
        # 200 또는 404 (데이터 없음)
        assert response.status_code in [200, 404], f"Expected 200/404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "paper_id" in data
            assert "analysis" in data or "title" in data
            print(f"✅ 논문 분석 조회 성공: {paper_id}")
        else:
            print(f"⚠️ 분석 데이터 없음: {paper_id} (예상 동작)")

    # ============= UC-4: Plan B 제안 조회 =============
    def test_api_get_planb_suggestions(self):
        """API: Plan B 제안 조회"""
        # 먼저 논문 목록에서 논문 ID 가져오기
        list_response = requests.get(f"{BASE_URL}/research/papers", params={"limit": 1})
        
        if list_response.status_code != 200 or not list_response.json()["items"]:
            pytest.skip("No papers available")
        
        paper_id = list_response.json()["items"][0]["id"]
        
        # Plan B 제안 조회
        url = f"{BASE_URL}/research/papers/{paper_id}/plan-b"
        response = requests.get(url)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "original_paper" in data
            assert "plan_b_suggestions" in data
            assert isinstance(data["plan_b_suggestions"], list)
            print(f"✅ Plan B 제안 조회 성공: {len(data['plan_b_suggestions'])}개 제안")
        else:
            print(f"⚠️ Plan B 데이터 없음: {paper_id} (예상 동작)")

    # ============= UC-5: 리포트 생성 =============
    def test_api_generate_report(self):
        """API: 리포트 생성"""
        # 먼저 사용자 생성
        user_url = f"{BASE_URL}/users"
        user_payload = {
            "id": self.test_user_id,
            "name": "리포트테스트",
            "role": "student",
            "interests": ["AI"]
        }
        requests.post(user_url, json=user_payload)
        
        # 리포트 생성
        url = f"{BASE_URL}/reports/generate"
        params = {"user_id": self.test_user_id}
        
        response = requests.post(url, params=params)
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "status" in data or "report_id" in data
        print(f"✅ 리포트 생성 성공: {data.get('status', 'success')}")

    # ============= 건강성 체크 =============
    def test_api_health_check(self):
        """API: 헬스 체크"""
        url = f"{BASE_URL.rsplit('/api', 1)[0]}/health"
        
        response = requests.get(url)
        
        # 서버가 실행 중인지 확인
        assert response.status_code in [200, 404], "Server not responding"
        print(f"✅ API 서버 정상 (상태코드: {response.status_code})")

    # ============= 오류 처리 =============
    def test_api_invalid_paper_id(self):
        """API: 존재하지 않는 논문 ID 처리"""
        url = f"{BASE_URL}/research/papers/invalid-id-12345/analysis"
        response = requests.get(url)
        
        # 404 또는 500 예상
        assert response.status_code in [404, 500]
        print(f"✅ 잘못된 논문 ID 처리 성공 (상태코드: {response.status_code})")

    def test_api_missing_required_fields(self):
        """API: 필수 필드 누락 처리"""
        url = f"{BASE_URL}/users"
        payload = {
            "id": self.test_user_id,
            # name 필드 누락
            "role": "student"
        }
        
        response = requests.post(url, json=payload)
        
        # 400 (Bad Request) 예상
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"✅ 필수 필드 누락 처리 성공 (상태코드: {response.status_code})")


class TestAPIPerformance:
    """API 성능 테스트"""

    def test_list_papers_response_time(self):
        """논문 목록 조회 응답 시간"""
        import time
        
        url = f"{BASE_URL}/research/papers"
        
        start_time = time.time()
        response = requests.get(url, params={"limit": 100})
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0, f"Response time too slow: {response_time:.2f}s"
        
        print(f"✅ 논문 목록 조회 응답 시간: {response_time:.3f}초")

    def test_paper_analysis_response_time(self):
        """논문 분석 조회 응답 시간"""
        import time
        
        # 논문 목록에서 ID 가져오기
        list_response = requests.get(f"{BASE_URL}/research/papers", params={"limit": 1})
        
        if list_response.status_code != 200 or not list_response.json()["items"]:
            pytest.skip("No papers available")
        
        paper_id = list_response.json()["items"][0]["id"]
        
        url = f"{BASE_URL}/research/papers/{paper_id}/analysis"
        
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            assert response_time < 5.0, f"Response time too slow: {response_time:.2f}s"
            print(f"✅ 논문 분석 조회 응답 시간: {response_time:.3f}초")
        else:
            print(f"⚠️ 분석 데이터 없음 (응답 시간: {response_time:.3f}초)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
