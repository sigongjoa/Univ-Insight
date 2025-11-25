#!/usr/bin/env python
"""
API Endpoint Screenshot Capture Tool

Captures screenshots of all 8 API endpoints and generates MD5 hashes
for verification and change detection.

Usage:
    python capture_screenshots.py
"""

import requests
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
ENDPOINTS_DIR = Path("endpoints")
ENDPOINTS_DIR.mkdir(exist_ok=True)

# API Endpoints to test
ENDPOINTS = [
    {
        "name": "1_universities_list",
        "method": "GET",
        "path": "/universities",
        "description": "GET /universities - List all universities"
    },
    {
        "name": "2_university_detail",
        "method": "GET",
        "path": "/universities/seoul-national-univ",
        "description": "GET /universities/{id} - Get university details"
    },
    {
        "name": "3_college_detail",
        "method": "GET",
        "path": "/colleges/snu-college-eng",
        "description": "GET /colleges/{id} - Get college details"
    },
    {
        "name": "4_department_detail",
        "method": "GET",
        "path": "/departments/snu-dept-computer",
        "description": "GET /departments/{id} - Get department details"
    },
    {
        "name": "5_professor_detail",
        "method": "GET",
        "path": "/professors/prof-choi-systems-001",
        "description": "GET /professors/{id} - Get professor details"
    },
    {
        "name": "6_lab_detail",
        "method": "GET",
        "path": "/laboratories/lab-systems-001",
        "description": "GET /laboratories/{id} - Get laboratory details"
    },
    {
        "name": "7_research_list",
        "method": "GET",
        "path": "/papers",
        "description": "GET /papers - List all research papers"
    },
    {
        "name": "8_research_analysis",
        "method": "GET",
        "path": "/papers/paper-snu-001/analysis",
        "description": "GET /papers/{id}/analysis - Get research paper analysis"
    }
]


def calculate_md5(data: str) -> str:
    """Calculate MD5 hash of data."""
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def capture_endpoint(endpoint: Dict) -> Tuple[bool, str, str]:
    """
    Capture endpoint response and save as JSON screenshot.

    Args:
        endpoint: Endpoint configuration dict

    Returns:
        Tuple of (success, content_hash, error_message)
    """
    url = f"{API_BASE_URL}{endpoint['path']}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Pretty print JSON
        data = response.json()
        content = json.dumps(data, indent=2, ensure_ascii=False)

        # Save to file
        screenshot_file = ENDPOINTS_DIR / f"{endpoint['name']}.json"
        screenshot_file.write_text(content, encoding='utf-8')

        # Calculate MD5 hash
        content_hash = calculate_md5(content)

        return True, content_hash, ""

    except requests.exceptions.RequestException as e:
        return False, "", str(e)
    except Exception as e:
        return False, "", f"Unexpected error: {str(e)}"


def generate_md5_report(results: List[Dict]) -> str:
    """Generate MD5 hash verification report."""
    report = []
    report.append("파일명                          MD5 Hash                         날짜         상태")
    report.append("────────────────────────────────────────────────────────────────────────────────")

    for result in results:
        if result['success']:
            status = "✅"
            hash_str = result['hash']
        else:
            status = "❌"
            hash_str = "ERROR"

        date_str = result['timestamp'].strftime("%Y-%m-%d %H:%M")
        name = f"{result['endpoint_name']}.json"

        report.append(f"{name:<32}{hash_str:<32}{date_str:<13}{status}")

    return "\n".join(report)


def run():
    """Run screenshot capture for all endpoints."""
    print("\n" + "=" * 80)
    print("📸 API 엔드포인트 스크린샷 캡처 시작")
    print("=" * 80)

    results = []
    successful = 0
    failed = 0

    for endpoint in ENDPOINTS:
        print(f"\n▶️  {endpoint['description']}")
        success, content_hash, error = capture_endpoint(endpoint)

        if success:
            print(f"   ✅ 성공 (Hash: {content_hash[:16]}...)")
            results.append({
                'endpoint_name': endpoint['name'],
                'success': True,
                'hash': content_hash,
                'timestamp': datetime.now()
            })
            successful += 1
        else:
            print(f"   ❌ 실패: {error}")
            results.append({
                'endpoint_name': endpoint['name'],
                'success': False,
                'hash': "",
                'timestamp': datetime.now()
            })
            failed += 1

    # Generate and save MD5 report
    print("\n" + "=" * 80)
    print("📊 MD5 해시 검증 결과")
    print("=" * 80)

    report = generate_md5_report(results)
    print(report)

    # Save to file
    report_file = ENDPOINTS_DIR / "md5_hashes.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("스크린샷 MD5 해시 검증 리포트\n")
        f.write(f"생성 날짜: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(report)

    # Save JSON results
    json_results = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": [
            {
                "endpoint": r['endpoint_name'],
                "success": r['success'],
                "hash": r['hash'],
                "timestamp": r['timestamp'].isoformat()
            }
            for r in results
        ]
    }

    json_file = ENDPOINTS_DIR / "screenshots_metadata.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 80)
    print(f"✅ 총 {successful}개 성공, ❌ {failed}개 실패")
    print(f"📁 파일 저장 위치: {ENDPOINTS_DIR.absolute()}/")
    print(f"📋 MD5 리포트: {report_file}")
    print(f"📊 메타데이터: {json_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run()
