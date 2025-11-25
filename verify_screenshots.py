#!/usr/bin/env python
"""
Screenshot Verification and Comparison Tool

Compares MD5 hashes of screenshots to detect changes.
Generates reports on screenshot integrity and changes over time.

Usage:
    python verify_screenshots.py
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
ENDPOINTS_DIR = Path("endpoints")
MD5_REPORT_FILE = ENDPOINTS_DIR / "md5_hashes.txt"
METADATA_FILE = ENDPOINTS_DIR / "screenshots_metadata.json"
HISTORY_FILE = ENDPOINTS_DIR / "screenshots_history.json"


def calculate_file_md5(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def verify_current_screenshots() -> Dict[str, str]:
    """Verify all current screenshot files and their hashes."""
    results = {}

    for json_file in ENDPOINTS_DIR.glob("*.json"):
        if json_file.name.startswith("screenshots_"):
            continue  # Skip metadata files

        # Read file content
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Calculate hash
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        results[json_file.name] = file_hash

    return results


def load_history() -> Dict:
    """Load screenshot history from file."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"versions": []}


def save_history(history: Dict):
    """Save screenshot history to file."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def compare_with_previous(current: Dict[str, str], history: Dict) -> Dict:
    """Compare current screenshots with previous version."""
    comparison = {
        "unchanged": [],
        "changed": [],
        "new": [],
        "removed": []
    }

    if not history["versions"]:
        # First version
        for filename in current:
            comparison["new"].append({
                "file": filename,
                "old_hash": None,
                "new_hash": current[filename]
            })
        return comparison

    # Get previous version
    previous = history["versions"][-1]["hashes"]

    for filename, current_hash in current.items():
        if filename not in previous:
            comparison["new"].append({
                "file": filename,
                "old_hash": None,
                "new_hash": current_hash
            })
        elif previous[filename] == current_hash:
            comparison["unchanged"].append({
                "file": filename,
                "hash": current_hash
            })
        else:
            comparison["changed"].append({
                "file": filename,
                "old_hash": previous[filename],
                "new_hash": current_hash
            })

    for filename in previous:
        if filename not in current:
            comparison["removed"].append({
                "file": filename,
                "hash": previous[filename]
            })

    return comparison


def generate_report(current: Dict[str, str], comparison: Dict) -> str:
    """Generate verification report."""
    report = []
    report.append("=" * 80)
    report.append("📊 스크린샷 검증 및 비교 리포트")
    report.append("=" * 80)
    report.append(f"\n생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary
    report.append("\n" + "=" * 80)
    report.append("📋 요약")
    report.append("=" * 80)
    report.append(f"✅ 총 스크린샷: {len(current)}개")
    report.append(f"✅ 변경 없음: {len(comparison['unchanged'])}개")
    report.append(f"⚠️  변경됨: {len(comparison['changed'])}개")
    report.append(f"✨ 신규: {len(comparison['new'])}개")
    report.append(f"❌ 삭제됨: {len(comparison['removed'])}개")

    # Detailed results
    report.append("\n" + "=" * 80)
    report.append("📁 파일별 상태")
    report.append("=" * 80)

    # Unchanged
    if comparison["unchanged"]:
        report.append("\n✅ 변경 없음:")
        for item in comparison["unchanged"]:
            report.append(f"   • {item['file']:<35} {item['hash'][:16]}...")

    # Changed
    if comparison["changed"]:
        report.append("\n⚠️  변경됨:")
        for item in comparison["changed"]:
            report.append(f"   • {item['file']:<35}")
            report.append(f"      이전: {item['old_hash'][:16]}...")
            report.append(f"      현재: {item['new_hash'][:16]}...")

    # New
    if comparison["new"]:
        report.append("\n✨ 신규 파일:")
        for item in comparison["new"]:
            report.append(f"   • {item['file']:<35} {item['new_hash'][:16]}...")

    # Removed
    if comparison["removed"]:
        report.append("\n❌ 삭제됨:")
        for item in comparison["removed"]:
            report.append(f"   • {item['file']:<35} {item['hash'][:16]}...")

    # Integrity check
    report.append("\n" + "=" * 80)
    report.append("🔐 무결성 검증")
    report.append("=" * 80)

    all_valid = all(hash for hash in current.values())
    if all_valid:
        report.append("✅ 모든 파일의 MD5 해시가 정상적으로 계산되었습니다.")
    else:
        report.append("❌ 일부 파일의 MD5 해시 계산에 실패했습니다.")

    # Recommendations
    report.append("\n" + "=" * 80)
    report.append("📌 권장사항")
    report.append("=" * 80)

    if comparison["changed"]:
        report.append(f"⚠️  {len(comparison['changed'])}개의 스크린샷이 변경되었습니다.")
        report.append("   변경 원인을 확인하고 필요한 경우 업데이트하세요.")

    if not comparison["changed"] and not comparison["new"]:
        report.append("✅ 모든 스크린샷이 이전 버전과 동일합니다.")

    report.append("\n" + "=" * 80 + "\n")

    return "\n".join(report)


def run():
    """Run screenshot verification."""
    # Verify current screenshots
    print("스크린샷 검증 중...")
    current = verify_current_screenshots()

    if not current:
        print("❌ 스크린샷 파일이 없습니다.")
        return

    # Load history
    history = load_history()

    # Compare with previous
    comparison = compare_with_previous(current, history)

    # Generate report
    report = generate_report(current, comparison)
    print(report)

    # Save report
    report_file = ENDPOINTS_DIR / "verification_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 검증 리포트 저장: {report_file}")

    # Update history
    history["versions"].append({
        "timestamp": datetime.now().isoformat(),
        "hashes": current
    })
    save_history(history)

    print(f"✅ 검증 히스토리 저장: {HISTORY_FILE}")

    # Print summary
    print("\n" + "=" * 80)
    print("📈 스크린샷 히스토리")
    print("=" * 80)
    print(f"총 버전: {len(history['versions'])}개")
    for i, version in enumerate(history["versions"], 1):
        print(f"{i}. {version['timestamp']}")


if __name__ == "__main__":
    run()
