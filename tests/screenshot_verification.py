#!/usr/bin/env python3
"""
스크린샷 검증 및 MD5 해시 비교 스크립트

이 스크립트는:
1. Playwright로 캡처한 스크린샷의 MD5 해시를 계산
2. 각 이미지가 고유한지 확인
3. 스크린샷 정보를 JSON으로 저장
4. 상세한 검증 리포트 생성
"""

import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class ScreenshotInfo:
    """스크린샷 정보"""
    page_name: str
    file_name: str
    file_path: str
    md5_hash: str
    file_size: int
    timestamp: str


class ScreenshotVerifier:
    """스크린샷 검증 클래스"""

    def __init__(self, screenshot_dir: str = 'screenshots'):
        self.screenshot_dir = Path(screenshot_dir)
        self.verification_file = self.screenshot_dir / 'verification.json'
        self.screenshots: List[ScreenshotInfo] = []

        # 디렉토리 생성
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def calculate_md5(self, file_path: str) -> str:
        """파일의 MD5 해시 계산"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def verify_screenshot(self, file_path: str, page_name: str) -> ScreenshotInfo:
        """스크린샷 파일 검증"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        # 파일 크기 확인
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ValueError(f"빈 파일입니다: {file_path}")

        # MD5 해시 계산
        md5_hash = self.calculate_md5(str(file_path))

        # 스크린샷 정보 생성
        info = ScreenshotInfo(
            page_name=page_name,
            file_name=file_path.name,
            file_path=str(file_path),
            md5_hash=md5_hash,
            file_size=file_size,
            timestamp=datetime.now().isoformat()
        )

        self.screenshots.append(info)
        return info

    def save_verification(self):
        """검증 정보를 JSON 파일로 저장"""
        data = [asdict(s) for s in self.screenshots]
        with open(self.verification_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_verification(self) -> List[ScreenshotInfo]:
        """저장된 검증 정보 로드"""
        if not self.verification_file.exists():
            return []

        with open(self.verification_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [ScreenshotInfo(**item) for item in data]

    def compare_screenshots(self) -> bool:
        """모든 스크린샷이 서로 다른지 확인"""
        hashes = [s.md5_hash for s in self.screenshots]
        unique_hashes = set(hashes)

        all_unique = len(unique_hashes) == len(hashes)

        print('\n🔍 스크린샷 MD5 해시 비교')
        print('═' * 80)

        if all_unique:
            print('✅ 모든 스크린샷이 서로 다릅니다!')
            print(f'   총 {len(hashes)}개의 고유한 이미지\n')
        else:
            print('⚠️ 중복된 스크린샷이 있습니다!')
            print(f'   총 {len(hashes)}개 중 {len(unique_hashes)}개가 고유함\n')

        # 해시 비교 테이블
        for i, ss1 in enumerate(self.screenshots):
            for j, ss2 in enumerate(self.screenshots):
                if i < j:
                    is_same = '동일' if ss1.md5_hash == ss2.md5_hash else '다름'
                    print(
                        f'{ss1.page_name.ljust(15)} vs '
                        f'{ss2.page_name.ljust(15)} : {is_same}'
                    )

        print('═' * 80)
        return all_unique

    def print_report(self):
        """검증 리포트 출력"""
        print('\n📋 스크린샷 검증 리포트')
        print('═' * 100)

        if not self.screenshots:
            print('검증된 스크린샷이 없습니다.')
            return

        # 헤더
        print(f'{"페이지명":<15} | {"파일명":<25} | {"파일 크기":<12} | {"MD5 해시":<32} | {"생성시간"}')
        print('─' * 100)

        # 데이터
        for ss in self.screenshots:
            timestamp = datetime.fromisoformat(ss.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(
                f'{ss.page_name:<15} | {ss.file_name:<25} | '
                f'{ss.file_size:>10} B | {ss.md5_hash} | {timestamp}'
            )

        print('═' * 100)

        # 통계
        total_size = sum(s.file_size for s in self.screenshots)
        print(f'\n📊 통계:')
        print(f'   총 파일 수: {len(self.screenshots)}')
        print(f'   총 파일 크기: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)')
        print(f'   검증 파일: {self.verification_file}')
        print(f'   스크린샷 디렉토리: {self.screenshot_dir.absolute()}')


def run_playwright_tests():
    """Playwright 스크린샷 테스트 실행"""
    print('🎬 Playwright 스크린샷 테스트 실행 중...\n')

    try:
        result = subprocess.run(
            ['npm', 'run', 'test:e2e', '--', 'screenshot-verification.spec.ts'],
            cwd='frontend',
            capture_output=True,
            text=True,
            timeout=300
        )

        print(result.stdout)
        if result.stderr:
            print('오류:', result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print('❌ 테스트 실행 시간 초과')
        return False
    except Exception as e:
        print(f'❌ 테스트 실행 중 오류: {e}')
        return False


def verify_existing_screenshots(screenshot_dir: str = 'frontend/screenshots'):
    """기존 스크린샷 파일 검증"""
    print('🔍 기존 스크린샷 검증 중...\n')

    verifier = ScreenshotVerifier(screenshot_dir)

    # PNG 파일 찾기
    png_files = list(Path(screenshot_dir).glob('*.png'))

    if not png_files:
        print(f'⚠️ {screenshot_dir}에서 PNG 파일을 찾을 수 없습니다.')
        return

    print(f'📸 발견된 스크린샷: {len(png_files)}개\n')

    # 각 파일 검증
    for png_file in sorted(png_files):
        try:
            page_name = png_file.stem.replace('-', ' ').title()
            info = verifier.verify_screenshot(str(png_file), page_name)

            print(f'✅ {info.page_name}')
            print(f'   파일: {info.file_name}')
            print(f'   크기: {info.file_size} bytes')
            print(f'   MD5: {info.md5_hash}\n')
        except Exception as e:
            print(f'❌ {png_file.name}: {e}\n')

    # 저장 및 보고서
    if verifier.screenshots:
        verifier.save_verification()
        verifier.print_report()
        verifier.compare_screenshots()
    else:
        print('❌ 검증된 스크린샷이 없습니다.')


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='스크린샷 MD5 해시 검증 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
예제:
  python screenshot_verification.py --run      # Playwright 테스트 실행
  python screenshot_verification.py --verify   # 기존 스크린샷 검증
  python screenshot_verification.py --both     # 둘 다 실행
        '''
    )

    parser.add_argument(
        '--run',
        action='store_true',
        help='Playwright 스크린샷 테스트 실행'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='기존 스크린샷 파일 검증'
    )
    parser.add_argument(
        '--both',
        action='store_true',
        help='테스트 실행 및 검증 모두 수행'
    )
    parser.add_argument(
        '--dir',
        default='frontend/screenshots',
        help='스크린샷 디렉토리 (기본값: frontend/screenshots)'
    )

    args = parser.parse_args()

    print('╔════════════════════════════════════════════════════════╗')
    print('║  스크린샷 MD5 해시 검증 도구                            ║')
    print('╚════════════════════════════════════════════════════════╝')

    if args.both:
        run_playwright_tests()
        verify_existing_screenshots(args.dir)
    elif args.run:
        run_playwright_tests()
    elif args.verify:
        verify_existing_screenshots(args.dir)
    else:
        # 기본 동작: 기존 스크린샷 검증
        verify_existing_screenshots(args.dir)


if __name__ == '__main__':
    main()
