from dataclasses import dataclass, field
from typing import List

@dataclass
class OptionsUI:
    url: str
    format: str
    container: str
    max_fragments: int
    output_path: str
    subtitle_langs: List[str] = field(default_factory=list)
    subtitle_only: bool = False
    subtitle_enabled: bool = False