from dataclasses import dataclass, field



@dataclass(slots=True)
class Data:
    USERNAME            : str            = 'olivercalazans'
    TOTAL_LANGS         : int            = 10
    lang_bytes          : dict[str, int] = field(default_factory=dict)
    len_repos           : int            = 0
    repos               : list[dict]     = field(default_factory=list)
    total_stars         : int            = 0
    total_commits       : int            = 0
    total_contributions : int            = 0