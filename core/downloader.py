#core.downloader.py

import sys

import yt_dlp
import pathlib

from PySide6.QtCore import QThread, Signal

from models.dataformat import YdlOptions
from models.download_options import OptionsUI


class DownloadThread(QThread):
    """
    yt_dlp 다운로드를 별도 스레드에서 수행
    - progress_signal: (percent, status_text)
    - finished_signal: 완료 메시지
    - error_signal: 오류 메시지
    """
    # 시그널
    progress_signal = Signal(float, str)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, options: OptionsUI):
        super().__init__()
        self.options = options
        self._is_canceled = False


    # -------------------------------------
    # 메인 실행 로직
    # -------------------------------------
    def run(self):
        # ffmpeg 모듈 경로
        ffmpeg_path = self._get_ffmpeg_path()
        if not ffmpeg_path:
            return

        url = self.options.url

        if Util.is_playlist(url):
            # playList 일때
            ydl_options = self._download_playlist(ffmpeg_path)
        else:
            # 단일 동영상 일떄.
            ydl_options = self._download_single(ffmpeg_path)

        if ydl_options is None:
            return

        ydl_opts = ydl_options.build()

        # 다운로드 실행
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.finished_signal.emit("다운로드 완료 ✅")
        except Exception as e:
            if "취소됨" in str(e):
                self.error_signal.emit("사용자가 다운로드를 취소했습니다.")
            else:
                self.error_signal.emit(f"다운로드 중 오류 발생: {e}")


    # -------------------------------------
    # 프로그래스 hook
    # -------------------------------------
    def _progress_hook(self, d):
        if self._is_canceled:
            raise Exception("사용자에 의해 다운로드 취소됨.")

        download_type, display_title = Util.parse_download_type_title(d)

        if d["status"] == "downloading":
            percent = d.get("_percent_str", "").replace("%", "").strip()
            if percent == 100:
                percent = 98
            self.progress_signal.emit(float(percent or 0), f"{download_type} 다운로드 중 : {display_title}")

        elif d["status"] == "finished":
            for p in range(90, 100):
                if self._is_canceled:
                    break
                self.progress_signal.emit(p, f"{download_type} 병합 중... : {display_title}")
                QThread.msleep(50)

            self.progress_signal.emit(100, f"{download_type} 병합 중... : {display_title}")


    def _download_single(self, ffmpeg_path) -> YdlOptions | None:
        # 단일 영상 다운로드.
        self.progress_signal.emit(0,  "영상 분석 중...")
        url = self.options.url
        requested_langs = self.options.subtitle_langs


        # 다운로드 할 자막이 있으면
        valid_langs = []
        if self.options.subtitle_enabled:
            valid_langs = Util.get_available_sub(url, requested_langs)
            if not valid_langs and self.options.subtitle_only:
                # 다운로드 할 자막이 존재하지 않고
                # 오직 자막만 다운로드 받으면 종료
                self.finished_signal.emit("선택한 자막 언어는 제공되지 않습니다.\n다운로드 할 자막이 없어 다운로드를 종료합니다.")
                return None

            self.progress_signal.emit(0, f"자막 다운로드 가능 언어: {', '.join(valid_langs)}")

        # ydl_opts
        return YdlOptions(
            out_dir=self.options.output_path,
            ffmpeg_path=ffmpeg_path,
            is_playlist=False,
            fmt=self.options.format,
            max_fragments=self.options.max_fragments,
            subtitle_only=self.options.subtitle_only,
            valid_langs=valid_langs,
            progress_hook=self._progress_hook,
        )

    # -------------------------------------
    # playlist Ydl_opt
    # -------------------------------------
    def _download_playlist(self, ffmpeg_path) -> YdlOptions | None:
        # 플레이리스트 다운
        self.progress_signal.emit(0, "플레이리스트 감지 중...")
        url = self.options.url
        requested_langs = self.options.subtitle_langs


        # 다운로드 할 자막이 있으면
        valid_langs = []
        if self.options.subtitle_enabled:
            # 자막 다운로드 할 경우
            valid_langs = requested_langs
            if not valid_langs and self.options.subtitle_only:
                # 자막막 다운로드인데, 요청 자막이 없으면
                self.finished_signal.emit("다운로드할 자막이 없어 종료합니다.")
                return None

        # ydl_opts
        return YdlOptions(
            out_dir=self.options.output_path,
            ffmpeg_path=ffmpeg_path,
            is_playlist=True,
            fmt=self.options.format,
            max_fragments=self.options.max_fragments,
            subtitle_only=self.options.subtitle_only,
            valid_langs=valid_langs,
            progress_hook=self._progress_hook,
        )



    # -------------------------------------
    # 다운로드 취소
    # -------------------------------------
    def cancel(self):
        """다운로드 중단"""
        print("다운로드 중단")
        self._is_canceled = True


    # -------------------------------------
    # ffmpeg 위치 가져오기
    # -------------------------------------
    def _get_ffmpeg_path(self) -> str:
        """ffmpeg 실행 경로 자동 탐지
        - 개발 환경: ./ffmpeg/ffmpeg.exe
        - 빌드 후 실행: exe와 같은 폴더 내 ffmpeg/ffmpeg.exe
        """
        if getattr(sys, 'frozen', False):
            base_dir = pathlib.Path(sys.executable).parent  # dist/YouTubeDownloader
        else:
            base_dir = pathlib.Path(__file__).resolve().parent.parent  # repo root

        ffmpeg_path = base_dir / "ffmpeg" / "ffmpeg.exe"

        if not ffmpeg_path.exists():
            self.error_signal.emit("⚠️ ffmpeg.exe를 찾을 수 없습니다.\n프로그램 폴더 내 'ffmpeg/ffmpeg.exe'가 존재해야 합니다.")
            return ""
        return str(ffmpeg_path)




class Util:
    # -------------------------------------
    #  다운로드하는 제목 형식 리턴 (타입, 보여질 이름)
    #  ex. "자막", "myVideo.ko.vtt"
    # -------------------------------------
    @staticmethod
    def parse_download_type_title(d) -> tuple[str, str]:
        info = d.get("info_dict", {}) or {}
        extension = info.get("ext")
        title = info.get("title", "알 수 없는 영상")
        filename = d.get("filename", "")

        # 파일명 및 타입 판별
        if extension == "vtt" or filename.endswith(".vtt"):
            download_type = "자막"
            display_title = filename.split("\\")[-1].rsplit(".", 1)[0]
        elif not extension:
            download_type = "알 수 없음"
            display_title = "알 수 없는 영상"
        else:
            download_type = "영상"
            display_title = title

        # 긴 제목은 줄바꿈 처리
        max_len = 50
        if len(display_title) > max_len:
            display_title = display_title[:max_len] + "\n" + display_title[max_len:]

        return download_type, display_title

    # -------------------------------------
    #  플래이 리스트인지 확인
    # -------------------------------------
    @staticmethod
    def is_playlist(url: str) -> bool:
        """
        URL이 단일 영상인지, 플레이리스트인지 판별한다.
        """
        if "playlist" in url:
            return True
        else:
            return False

    # -------------------------------------
    #  실제 존재하는 자막만 반환
    # -------------------------------------
    @staticmethod
    def get_available_sub(url, requested_langs):
        """yt_dlp로 영상 메타데이터 확인 후, 실제 존재하는 자막만 반환"""
        try:
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                available = set(info.get("subtitles", {}).keys())
                return [lang for lang in requested_langs if lang in available]
        except Exception:
            return []