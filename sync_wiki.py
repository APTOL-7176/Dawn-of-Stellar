#!/usr/bin/env python3
"""
GitHub Wiki 동기화 스크립트
로컬 docs/wiki 폴더의 내용을 GitHub Wiki로 자동 동기화합니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import time
import requests
from typing import List, Dict, Optional

class GitHubWikiSync:
    def __init__(self, repo_owner: str = "APTOL-7176", repo_name: str = "Dawn-of-Stellar"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.wiki_repo_url = f"https://github.com/{repo_owner}/{repo_name}.wiki.git"
        self.local_wiki_path = Path("docs/wiki")
        self.temp_wiki_path = Path("temp_wiki_clone")
        
    def check_dependencies(self) -> bool:
        """필요한 의존성 확인"""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            print("✅ Git이 설치되어 있습니다.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Git이 설치되어 있지 않습니다. Git을 먼저 설치해주세요.")
            return False
    
    def clone_wiki_repo(self) -> bool:
        """GitHub Wiki 저장소 클론"""
        try:
            if self.temp_wiki_path.exists():
                shutil.rmtree(self.temp_wiki_path)
            
            print(f"📂 GitHub Wiki 저장소를 클론합니다: {self.wiki_repo_url}")
            result = subprocess.run([
                "git", "clone", self.wiki_repo_url, str(self.temp_wiki_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Wiki 저장소 클론 완료")
                return True
            else:
                print(f"❌ Wiki 저장소 클론 실패: {result.stderr}")
                # Wiki가 없는 경우 새로 생성
                if "not found" in result.stderr.lower():
                    print("📝 새로운 Wiki 저장소를 초기화합니다...")
                    return self.init_wiki_repo()
                return False
        except Exception as e:
            print(f"❌ 클론 중 오류 발생: {e}")
            return False
    
    def init_wiki_repo(self) -> bool:
        """새로운 Wiki 저장소 초기화"""
        try:
            os.makedirs(self.temp_wiki_path, exist_ok=True)
            os.chdir(self.temp_wiki_path)
            
            # Git 초기화
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "remote", "add", "origin", self.wiki_repo_url], check=True)
            
            # 첫 번째 페이지 생성
            with open("Home.md", "w", encoding="utf-8") as f:
                f.write("# Dawn of Stellar Wiki\n\n위키를 초기화하는 중입니다...")
            
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Initialize wiki"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "master"], check=True)
            
            os.chdir("..")
            print("✅ Wiki 저장소 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ Wiki 초기화 실패: {e}")
            os.chdir("..")
            return False
    
    def sync_files(self) -> bool:
        """로컬 파일을 Wiki 저장소로 동기화"""
        try:
            if not self.local_wiki_path.exists():
                print("❌ 로컬 wiki 폴더가 존재하지 않습니다.")
                return False
            
            # 기존 파일 제거 (media 폴더 제외)
            for item in self.temp_wiki_path.iterdir():
                if item.name not in [".git", "media"] and item.is_file():
                    item.unlink()
            
            # 로컬 파일 복사
            copied_files = []
            for md_file in self.local_wiki_path.glob("*.md"):
                dest_file = self.temp_wiki_path / md_file.name
                shutil.copy2(md_file, dest_file)
                copied_files.append(md_file.name)
                print(f"📄 복사됨: {md_file.name}")
            
            # media 폴더 복사 (있는 경우)
            local_media = self.local_wiki_path / "media"
            if local_media.exists():
                dest_media = self.temp_wiki_path / "media"
                if dest_media.exists():
                    shutil.rmtree(dest_media)
                shutil.copytree(local_media, dest_media)
                print("📁 media 폴더 복사 완료")
            
            print(f"✅ {len(copied_files)}개 파일 동기화 완료")
            return True
        except Exception as e:
            print(f"❌ 파일 동기화 실패: {e}")
            return False
    
    def convert_links(self) -> bool:
        """로컬 링크를 GitHub Wiki 링크로 변환"""
        try:
            for md_file in self.temp_wiki_path.glob("*.md"):
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 로컬 링크를 GitHub Wiki 링크로 변환
                # docs/wiki/파일명.md -> 파일명 (확장자 제거)
                import re
                content = re.sub(r'docs/wiki/([^)]+)\.md', r'\1', content)
                
                # media 링크를 GitHub Wiki 형식으로 변환
                content = re.sub(r'media/([^)]+)', r'https://github.com/APTOL-7176/Dawn-of-Stellar/wiki/media/\1', content)
                
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print(f"🔗 링크 변환 완료: {md_file.name}")
            
            return True
        except Exception as e:
            print(f"❌ 링크 변환 실패: {e}")
            return False
    
    def commit_and_push(self) -> bool:
        """변경사항 커밋 및 푸시"""
        try:
            os.chdir(self.temp_wiki_path)
            
            # 변경사항 확인
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if not result.stdout.strip():
                print("📝 변경사항이 없습니다.")
                os.chdir("..")
                return True
            
            # 커밋 및 푸시
            subprocess.run(["git", "add", "."], check=True)
            commit_message = f"Wiki 자동 동기화 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)
            
            os.chdir("..")
            print("✅ GitHub Wiki에 변경사항이 푸시되었습니다!")
            return True
        except Exception as e:
            print(f"❌ 커밋/푸시 실패: {e}")
            os.chdir("..")
            return False
    
    def cleanup(self):
        """임시 파일 정리"""
        if self.temp_wiki_path.exists():
            shutil.rmtree(self.temp_wiki_path)
            print("🧹 임시 파일 정리 완료")
    
    def sync(self) -> bool:
        """전체 동기화 프로세스 실행"""
        print("🚀 GitHub Wiki 동기화를 시작합니다...")
        
        try:
            if not self.check_dependencies():
                return False
            
            if not self.clone_wiki_repo():
                return False
            
            if not self.sync_files():
                return False
            
            if not self.convert_links():
                return False
            
            if not self.commit_and_push():
                return False
            
            print("🎉 GitHub Wiki 동기화가 완료되었습니다!")
            return True
        
        finally:
            self.cleanup()

def main():
    """메인 함수"""
    print("=" * 60)
    print("🌟 Dawn of Stellar - GitHub Wiki 동기화 도구")
    print("=" * 60)
    
    sync_tool = GitHubWikiSync()
    
    # 사용자 확인
    response = input("GitHub Wiki로 동기화하시겠습니까? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ 동기화가 취소되었습니다.")
        return
    
    # 동기화 실행
    success = sync_tool.sync()
    
    if success:
        print("\n✅ 동기화 완료! GitHub Wiki를 확인해보세요:")
        print(f"🔗 https://github.com/APTOL-7176/Dawn-of-Stellar/wiki")
    else:
        print("\n❌ 동기화 실패. 오류 메시지를 확인해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
