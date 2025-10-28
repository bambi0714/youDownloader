# models.dataformat.py

import os
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class YdlOptions:
    out_dir: str
    ffmpeg_path: str
    is_playlist: bool
    fmt: str
    max_fragments: int
    subtitle_only: bool = False
    valid_langs: list[str] = field(default_factory=list)
    progress_hook: Callable[[dict[str, Any]], None] | None = None

    def build(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "outtmpl": os.path.join(self.out_dir, f"%(title)s_%(height)sp.%(ext)s"),
            "quiet": True,
            "noplaylist": not self.is_playlist,
            "ffmpeg_location": self.ffmpeg_path,
        }

        if self.progress_hook:
            opts["progress_hooks"] = [self.progress_hook]

        # 자막 존재 시
        if self.valid_langs:
            opts.update({
                "writesubtitles": True,
                "subtitleslangs": self.valid_langs,
                "skip_auto_subtitle": True,
            })

        # 자막만 다운 시
        if self.subtitle_only:
            opts.update({
                "skip_download": True,
                "outtmpl": os.path.join(self.out_dir, "%(title)s.%(ext)s"),
            })
        else:
            opts.update({
                "format": self.fmt,
                "concurrent_fragment_downloads": self.max_fragments,
            })

        return opts


# @dataclass
# class VideoInfo:
#     id: str
#     url: str
#     title: str
#     # duration: Optional[int] = None
#     # thumbnails: List[Dict[str, Any]] = field(default_factory=list)
#     formats: List[Dict[str, Any]] = field(default_factory=list)
#     subtitles: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
#     ext: Optional[str] = None