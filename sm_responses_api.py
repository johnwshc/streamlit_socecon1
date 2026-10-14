from functools import reduce

from bls_api import BLS_API_KEY, SMResponse, BuildSMResponse, SMIdResults, ParseBlsSmSid, BuildSMIdResults,SMResult,SMData, PeriodData
from dataclasses import dataclass
from typing import List, Dict, Union, Optional
import json
from pathlib import Path
import pandas as pd


@dataclass
class SMBlsResponses:
    good_responses: List[SMResponse]
    meta_dict: List[Dict]

class BuildSMResponses:

    def __init__(self):
        self.ids_dir = Path("data/bls_api")
        self.good_ffns = self.load_good_id_filenames()
        # self.j_obj = self.load_good_ids_file(self.ffn)
        #
        self.good_responses: List[SMResponse] = []
        self.load_ids_files()
        self.remove_dups()
        self.meta_dict: List[Dict] = self.build_meta_dict()

    def build_meta_dict(self) -> List[Dict]:
        rsums = []
        for r in self.good_responses:
            ind_des = r.ind_desc
            results: SMIdResults = r.results

            sid_u = results.r_ids[0].get('ser_id', None)
            # print(f"sid_u: {sid_u}")
            sid_u_data = results.r_ids[0].get('data', None)
            sid_s = results.r_ids[1].get('ser_id', None)
            # print(f"sid_s: {sid_s}")
            sid_s_data = results.r_ids[1].get('data', None)
            ind_id = ParseBlsSmSid(sid_s).super_ind
            # print(f"ind_desc: {r.ind_desc}")
            # print(f"ind_id: {ind_id}")
            rsum = {'sid_u':sid_u, 'sid_u_data': sid_u_data, 'sid_s': sid_s, 'sis_s_data': sid_s_data, 'ind_id': ind_id, 'ind_desc': r.ind_desc}
            rsums.append(rsum)
        return rsums

    def load_good_id_filenames(self) -> List[str]:

        names = [
            path.name
            for path in self.ids_dir.iterdir()
            if path.is_file()
               and path.name.startswith("good")
               and path.name.endswith(".json")
        ]
        return [Path(self.ids_dir, name).as_posix() for name in names]

    def load_ids_files(self):
        responses = []
        for fn in self.good_ffns:
            with (open(fn, 'r') as f):
                j_obj = json.load(f)
            for obj in j_obj:
                resp = obj['raw']
                responses.append(BuildSMResponse(resp).build())
            self.good_responses.extend(responses)
            responses = []

    def remove_dups(self):
        no_dupes = []
        for resp in self.good_responses:
            if resp.ind_desc not in [r.ind_desc for r in no_dupes]:
                no_dupes.append(resp)
        self.good_responses = no_dupes


    def build(self) -> SMBlsResponses:

        return SMBlsResponses(good_responses=self.good_responses, meta_dict=self.meta_dict)


class BeaNaicsCon:
    bls_naics_fn: Path = Path('data/bea_naics_concordance.txt')

    def __init__(self, fn: Path=bls_naics_fn):

        self.items = []
        with open(fn.as_posix(), 'r') as f:
            lines = f.readlines()

        for line in lines:
            line_code = line[0:4]
            raw_ind_desc = line[4:]

            if not line_code.isdigit() or len(line_code) != 4:
                raise ValueError(f"Invalid line code: {line_code}")

            self.items.append({
                "line_code": line_code,
                "ind_desc": raw_ind_desc,
            })

        self.dd = self.build_bea_naics_dict()
        self.df = pd.DataFrame(self.dd)

    def get_level(self, ind_desc):
        import unicodedata

        s = ind_desc  # "1010     Manufacturing"
        # print(s)
        num_spaces = 0
        for i, ch in enumerate(s):
            if ch.isspace():
                num_spaces += 1
                print(i, repr(ch), unicodedata.name(ch, "<no name>"))
                continue
            else:
               break  #  print(i, repr(ch), unicodedata.name(ch, "<no name>"))

        return num_spaces

    def get_naics(self, ind_desc):
        ss = ind_desc
        naics = ss.split()[-1]
        return naics

    def get_desc(self, ind_desc):
        desc_ar = ind_desc.split()
        return " ".join(desc_ar[:-1])

    # bea_naics_con: BeaNaicsCon = BeaNaicsCon()
    def build_bea_naics_dict(self):
        new_items = []
        for item in self.items:
            ind_desc = item["ind_desc"]
            level = self.get_level(item["ind_desc"])
            naics = item["ind_desc"].split()[-1]
            clean_desc = self.get_desc(ind_desc)

            dd = {"line_code": item["line_code"],
                  "ind_desc": clean_desc,
                  "level": level,
                  "naics": naics
                  }
            # print(f"line_code: {dd['line_code']}, level == {level}")
            new_items.append(dd)
        return new_items




