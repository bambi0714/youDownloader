#mian.py

import sys
import time

from PySide6.QtWidgets import QApplication
from ui.browser import BrowserWindow

# def main():
#
    # print("🎬 유튜브 다운로드 프로그램 (콘솔 버전)")
    # url = input("다운로드할 유튜브 URL을 입력하세요: ").strip()
    #
    # video_type = analyze_url(url)
    # print(f"🔍 URL 분석 결과: {video_type}")
    #
    # save_path = os.path.join(os.getcwd(), "downloads")
    # os.makedirs(save_path, exist_ok=True)
    #
    # downloader = YouTubeDownloader(url, save_path, video_type)
    # downloader.download()
    # app = QApplication(sys.argv)
    # win = BrowserWindow() ffmpeg/ffmpeg.exe
    # pyinstaller --noconfirm --onefile --windowed ^
# --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" ^
# --name "YouTubeDownloader" main.py
    # win.show()
    # sys.exit(app.exec())

def main():
    start_time = time.time()
    app = QApplication(sys.argv)
    win = BrowserWindow()
    win.show()
    elapsed = time.time() - start_time
    print(f"[INFO] GUI 창 표시까지{elapsed  :.2f}초 걸림")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
