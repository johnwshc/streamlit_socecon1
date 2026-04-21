import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Optional


@dataclass
class LCMeta:
    LineCode: int
    Description: str
    Rank: int


    @classmethod
    def parse_line(cls, line: str):
        """Parse a line like '12\t   Some text' into components.

        Returns a dict with keys:
          - LineCode: int (the leading digits)
          - rank: int (number of spaces between the tab and the first non-space char)
          - text: str (the text with leading/trailing whitespace removed)

        The function is permissive: it first tries the exact 'digits + tab + spaces + text'
        pattern, then falls back to 'digits + whitespace + text'. If the line doesn't
        match, returns None.
        """
        if line is None:
            return None
        # Remove trailing newline but keep trailing internal spaces for counting
        ln = line.rstrip('\n')

        # Primary pattern: digits, a tab, then N spaces, then text
        m = re.match(r"^(\d+)\t( *)(.*)$", ln)
        if m:
            linecode = int(m.group(1))
            spaces = len(m.group(2))
            text = m.group(3).rstrip()
            lc_meta = LCMeta(LineCode=linecode, Description=text, Rank=spaces)

            return lc_meta
        else:
            return None


@dataclass
class LCIndex:
    lcx_codes: List[LCMeta]

    @classmethod
    def parse_codes(cls, fn="data/ND2/gdp_classes.txt"):
        # alt = data/gdp_short_classes.txt
        lc_codes: List[LCMeta] = []
        data_fn = fn
        # if not in same dir, fall back to data/ND2/gdp_classes.txt
        if not Path(data_fn).exists():
            print(f"Could not find {data_fn}")
            return None

        print(f"Parsing {data_fn}")

        with open(data_fn) as f:
            lines = f.read().splitlines()
            print(f"Read {len(lines)} lines from {data_fn}")

        # show first two lines (ln0, ln1) and a small sample
        for line in lines:
            parsed: LCMeta|None = LCMeta.parse_line(line)
            if not parsed:
                print("Could not parse line '%s'" % line)
            lc_codes.append(parsed)
        return LCIndex(lc_codes)

    def get_lc(self, desc):
        for code in self.lcx_codes:
            if code.Description == desc:
                return code.LineCode
        else:
            return None

    def get_desc(self, lc: int):
        for code in self.lcx_codes:
            if code.LineCode == lc:
                return code.Description
        else:
            return None

    def get_rank(self, lc):
        for code in self.lcx_codes:
            if code.LineCode == lc:
                return code.Rank
        else:
            return None
