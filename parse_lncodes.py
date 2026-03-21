import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from pydantic import BaseModel


class LCMeta(BaseModel):
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
            lc_index = LCMeta(LineCode=linecode, Description=text, Rank=spaces)

            return lc_index
        else:
            return None



    @classmethod
    def parse_codes(cls):
        lc_codes: List[LCIndex] = []
        data_fn = Path(__file__).with_name("gdp_classes.txt")
        # if not in same dir, fall back to data/ND2/gdp_classes.txt
        if not data_fn.exists():
            data_fn = Path(__file__).parent / "data" / "ND2" / "gdp_classes.txt"

        if not data_fn.exists():
            print("Could not find gdp_classes.txt next to this script or in data/ND2/")
            return None

        lines = data_fn.read_text(encoding='utf-8').splitlines()

        # show first two lines (ln0, ln1) and a small sample
        for line in lines:
            parsed: LCIndex = cls.parse_line(line)
            if not parsed:
                print("Could not parse line '%s'" % line)
            lc_codes.append(parsed)
        return lc_codes


class LCIndex(BaseModel):
    lc_metas: List[LCMeta]

    def find_lc(self, desc: str) -> Optional[LCMeta]:
        """Find the LCMeta with the given description, ignoring leading/trailing whitespace.

        Returns the LCMeta if found, or None if not found.
        """
        desc = desc.strip()
        for meta in self.lc_metas:
            if meta.Description.strip() == desc:
                return meta
        return None

    def find_desc(self, lc: int) -> Optional[LCMeta]:
        """Find the LCMeta with the given description, ignoring leading/trailing whitespace. """
        for meta in self.lc_metas:
            if meta.LineCode  == lc:
                return meta
        else:
            return None


