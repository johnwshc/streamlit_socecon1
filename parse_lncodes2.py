import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LCMeta:
    LineCode: int
    Description: str
    Rank: int

@dataclass
class LCIndex:
    lcx: List[LCMeta]

    def get_description(self, lc:int) -> str|None:
        for meta in self.lcx:
            if meta.LineCode == lc:
                return meta.Description
        return None





def parse_line_to_dict(line: str) -> Optional[Dict[str, object]]:
    """Parse a single line like '12\t   Some text' and return a dict with keys:
      - 'LineCode': int
      - 'Rank': int (number of spaces between the tab and the first non-space char)
      - 'Description': str (text part with trailing whitespace removed)

    Behavior:
      - Primary pattern expects digits + TAB + (0-5) spaces + text.
      - Falls back to digits + whitespace + text if a TAB is not present.
      - Returns None for blank or unparseable lines.
    """
    if line is None:
        return None
    ln = line.rstrip('\n')
    if not ln.strip():
        return None

    # Primary: digits, tab, then N spaces (0..5 typically), then text
    m = re.match(r"^(\d+)\t(\s{0,5})(.*)$", ln)
    if m:
        linecode = int(m.group(1))
        spaces = len(m.group(2))
        desc = m.group(3).rstrip()
        return {"LineCode": linecode, "Rank": spaces, "Description": desc}

    # Fallback: digits followed by whitespace (no tab)
    m2 = re.match(r"^(\d+)(\s+)(.*)$", ln)
    if m2:
        linecode = int(m2.group(1))
        # count only the spaces immediately after the digits (tabs count as one char)
        spacer = m2.group(2)
        # treat tabs in fallback as zero for Rank, but count spaces
        spaces = spacer.count(' ')
        desc = m2.group(3).rstrip()
        return {"LineCode": linecode, "Rank": spaces, "Description": desc}

    return None


def find_gdp_file(preferred: Optional[str] = None) -> Optional[Path]:
    """Locate gdp_classes.txt or gdp_short_classes.txt.

    Search order:
      1. If `preferred` provided and exists, return it.
      2. Look for files next to this script.
      3. Look in ./data/ND2/ under project root.
    """
    here = Path(__file__).parent
    candidates = []
    if preferred:
        candidates.append(here / preferred)
        candidates.append(here / 'data' / 'ND2' / preferred)

    candidates.extend([
        here / 'gdp_short_classes.txt',
        here / 'gdp_classes.txt',
        here / 'data' / 'ND2' / 'gdp_short_classes.txt',
        here / 'data' / 'ND2' / 'gdp_classes.txt',
    ])

    for p in candidates:
        if p and p.exists():
            return p
    return None


def parse_file(path: Path) -> LCIndex:
    """Parse the file at `path` and return a list of dicts per line.

    Lines that cannot be parsed are skipped.
    """
    text = path.read_text(encoding='utf-8')
    results: List[Dict[str, object]] = []
    for i, ln in enumerate(text.splitlines(), start=1):
        parsed = parse_line_to_dict(ln)
        if parsed is None:
            # skip blank or unparseable lines
            continue
        results.append(parsed)
    metas: List[LCMeta] = [LCMeta(**d) for d in results]
    return LCIndex(lcx=metas)


def parse_default(preferred: Optional[str] = None) -> Optional[List[Dict[str, object]]]:
    p = find_gdp_file(preferred)
    if not p:
        print("Could not find gdp_classes.txt or gdp_short_classes.txt")
        return None
    return parse_file(p)


if __name__ == '__main__':
    # small CLI demo when run directly
    p = find_gdp_file()
    if not p:
        print('No gdp file found nearby.')
    else:
        print('Parsing', p)
        rows = parse_file(p)
        print(f'Parsed {len(rows)} entries. Sample:')
        for r in rows[:10]:
            print(r)


