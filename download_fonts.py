import os
import urllib.request
import zipfile
import io

def download_fonts():
    """Noto Sans KR 폰트를 다운로드하고 설치합니다."""
    # 폰트 디렉토리 생성
    font_dir = os.path.join('static', 'fonts')
    os.makedirs(font_dir, exist_ok=True)
    
    # Noto Sans KR 폰트 다운로드 URL
    font_url = 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/NotoSansCJKkr-VF.ttf'
    
    try:
        # 폰트 파일 다운로드
        print('Noto Sans KR 폰트 다운로드 중...')
        urllib.request.urlretrieve(font_url, os.path.join(font_dir, 'NotoSansKR-Regular.ttf'))
        print('폰트 설치 완료!')
    except Exception as e:
        print(f'폰트 다운로드 중 오류 발생: {str(e)}')

if __name__ == '__main__':
    download_fonts() 