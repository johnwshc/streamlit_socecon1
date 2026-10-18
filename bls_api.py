import requests
import time
from pydantic import BaseModel, Field
import pandas as pd
from pathlib import Path
import json
import prettytable
from typing import List
from dataclasses import dataclass

BLS_API_KEY = '69644205dd1b4acf91b2acb0570a82bc'

def sample_bls1_api():
    """ sample api call for state employment"""

    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['CUUR0000SA0', 'SUUR0000SA0'], "startyear": "2011", "endyear": "2014"})
    p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    out_dir = 'data\\bls_api\\bls_query_data\\'
    for series in json_data['Results']['series']:
        x = prettytable.PrettyTable(["series id", "year", "period", "value", "footnotes"])
        seriesId = series['seriesID']
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes = footnotes + footnote['text'] + ','

            if 'M01' <= period <= 'M12':
                x.add_row([seriesId, year, period, value, footnotes[0:-1]])
        output = open(out_dir + seriesId + '.txt', 'w')
        output.write(x.get_string())
        output.close()


def sample_bls2_api():
    """ sample 2 api call to state employment api bls """

    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['SMU54000003000000001'], "startyear": "2015", "endyear": "2024"})
    p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    for series in json_data['Results']['series']:
        x = pd.DataFrame(data=None, index=None, columns=["seriesid", "year", "period", "value", "footnotes"])
        seriesId = series['seriesID']
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes = footnotes + footnote['text'] + ','

            if 'M01' <= period <= 'M12':
                new_row = pd.DataFrame([{
                    "seriesid": seriesId,
                    "year": year,
                    "period": period,
                    "value": value,
                    "footnotes": footnotes,
                }])
                x = pd.concat([x, new_row], ignore_index=True)

        return x
class Prefixes:
    prefix_data_fn = 'data/bls_api/prefixes.json'
    dd = {'EN': 'State and county wages and employment',
          'SM': 'State and Area Employment by Industry, Hours, and Earnings',
          'CE': 'National Employment Hours  earnings',
          'LA': 'local Area Unemployment',
          'BD': 'Business Employment Dynamics Statistics',
          'JT': 'Job Openings and Labor Turnover',
          'AP': 'Average Prices',
          'CU': 'Consumper Price index -- all consumers',
          'CW': 'Consumer Price index -- wage workers',
          'PR': 'Productivity',
          'WS': 'Work stoppages',
          'NB': 'National Pay and Benefits',
          'TU': 'Time and Use Survey',
          'CX': 'Consumer Expenditures',
          'IP': 'Industry Productivity',
          'IS': 'Workplace injury',
          }

    def __init__(self):
        if Path(Prefixes.prefix_data_fn).exists():
            self.prefix_dd = json.load(open(Prefixes.prefix_data_fn))
        else:
            Prefixes.create_data_fle()
            self.prefix_dd = json.load(open(Prefixes.prefix_data_fn))

    def get_prefix_description(self, prefix) ->str|None:
        return self.prefix_dd.get(prefix, None)

    @classmethod
    def create_data_fle(cls):
        with open(Prefixes.prefix_data_fn, 'w') as f:
            json.dump(Prefixes.dd, f)

class SupersectorData:
    """ super sector data and utils for bls api """
    ddir = 'data/bls_api/supers.txt'

    def __init__(self, ddir=ddir):
        self.ddir = ddir
        self.super_df = self.load_data()
        self.super_code_dict = self.get_super_code_dict()
        self.super_name_dict = self.get_super_name_dict()

    def get_super_code_dict(self):
        super_df = self.super_df.set_index('supersector_name', drop=True)
        super_dict  = super_df.to_dict()
        sdd = super_dict.get('supersector_code', None)
        return sdd

    def get_super_name_dict(self):
        super_df = self.super_df.set_index('supersector_code', drop=True)
        super_dict  = super_df.to_dict()
        sdd = super_dict.get('supersector_name', None)
        return sdd

    def load_data(self):
        super_data = []
        with open(self.ddir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                tparts = tuple(parts)
                super_data.append(tparts)

        ssdata = list(super_data[1:].copy())
        sdata_cols = list(super_data[0])
        dd = {sdata_cols[0]: [s[0] for s in ssdata],
              sdata_cols[1]: [s[1] for s in ssdata]}

        super_df = pd.DataFrame(dd)
        return super_df

    def find_super_code(self, super_name: str) -> str:
       return self.super_code_dict.get(super_name, None)

    def find_super_name(self, super_code: str) -> str:
        return self.super_name_dict.get(super_code, None)


class IndustryData:
    """ industry data and utils for bls api """

    ddir = 'data/bls_api/industries.txt'
    def __init__(self, ddir=ddir):
        self.ddir = ddir
        self.industries_df = self.load_data()
        self.industries_code_dict = self.industries_df.set_index('industry_code',
                                                                 drop=True).to_dict()
        self.industries_name_dict = self.industries_df.set_index('industry_name',
                                                                 drop=True).to_dict()

    def load_data(self):
        industries_data = []
        with open(self.ddir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                tparts = tuple(parts)
                industries_data.append(tparts)
        industries_cols = list(industries_data[0])
        industries_data = list(industries_data[1:].copy())


        dd = {industries_cols[0]: [s[0] for s in industries_data],
              industries_cols[1]: [s[1] for s in industries_data]}

        industries_df = pd.DataFrame(dd)
        return industries_df




    def find_industries_code(self, ind_name: str) -> str|None:
        return self.industries_name_dict.get(ind_name)

    def find_industries_name(self, ind_code: str) -> str|None:
        return self.industries_name_dict.get(ind_code)





class StateData:
    """ state data and utils for bls api """

    ddir = 'data/bls_api/states.txt'
    def __init__(self, ddir=ddir):
        self.ddir = ddir
        self.states_df = self.load_data()
        self.states_code_dict = self.get_states_code_dict()
        self.states_name_dict = self.get_states_name_dict()


    def load_data(self):
        states_data = []
        with open(self.ddir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                tparts = tuple(parts)
                states_data.append(tparts)
        states_cols = list(states_data[0])
        states_data = list(states_data[1:].copy())


        dd = {states_cols[0]: [s[0] for s in states_data],
              states_cols[1]: [s[1] for s in states_data]}
        states_df = pd.DataFrame(dd)
        return states_df

    def get_states_code_dict(self):
        states_df = self.states_df.set_index('state_name', drop=True)
        states_dict = states_df.to_dict()
        sdd = states_dict.get('state_code', None)
        return sdd

    def get_states_name_dict(self):
        states_df = self.states_df.set_index('state_code', drop=True)
        states_dict = states_df.to_dict()
        sdd = states_dict.get('state_name', None)
        return sdd

    def find_state_code(self, state_name: str) -> str:
        return self.states_code_dict.get(state_name, None)

    def find_state_name(self, state_code: str) -> str:
        return self.states_name_dict.get(state_code, None)



class AreaData:
    """ area data and utils for bls api """

    ddir = 'data/bls_api/areas.txt'
    def __init__(self, ddir=ddir):
        self.ddir = ddir
        self.areas_df = self.load_data()
        self.areas_code_dict = self.get_areas_code_dict()
        self.areas_name_dict = self.get_areas_name_dict()

    def get_areas_code_dict(self):
        areas_code_df = self.areas_df.set_index('area_name', drop=True)
        areas_code_dict  = areas_code_df.to_dict()
        sdd = areas_code_dict.get('area_code', None)
        return sdd

    def get_areas_name_dict(self):
        areas_name_df = self.areas_df.set_index('area_code', drop=True)
        areas_name_dict  = areas_name_df.to_dict()
        sdd = areas_name_dict.get('area_name', None)
        return sdd

    def load_data(self):
        areas_data = []
        with open(self.ddir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                tparts = tuple(parts)
                areas_data.append(tparts)

            areas_cols = list(areas_data[0])
            areas_data = list(areas_data[1:].copy())

            dd = {areas_cols[0]: [s[0] for s in areas_data],
                  areas_cols[1]: [s[1] for s in areas_data]}

            areas_df = pd.DataFrame(dd)
            return areas_df

    def find_area_code(self, area_name: str) -> str:
        return self.areas_code_dict.get(area_name, None)
    def find_area_name(self, area_code: str) -> str:
        return self.areas_name_dict.get(area_code, None)


class DataTypes:
    """ data type data and utils for bls api """
    ddir = 'data/bls_api/data_types.txt'

    def __init__(self, ddir=ddir):
        self.ddir = ddir
        self.dt_df = self.load_data()
        self.dt_code_dict = self.get_dt_code_dict()
        self.dt_name_dict = self.get_dt_name_dict()

    def get_dt_code_dict(self):
        dt_code_df = self.dt_df.set_index('data_type_text', drop=True)
        dt_code_dict = dt_code_df.to_dict()
        sdd = dt_code_dict.get('data_type_code', None)
        return sdd

    def get_dt_name_dict(self):
        dt_name_df = self.dt_df.set_index('data_type_code', drop=True)
        dt_name_dict = dt_name_df.to_dict()
        sdd = dt_name_dict.get('data_type_text', None)
        return sdd

    def load_data(self):
        dt_data = []
        with open(self.ddir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.split('\t')
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                tparts = tuple(parts)
                dt_data.append(tparts)

            dt_cols = list(dt_data[0])
            dt_data = list(dt_data[1:].copy())

            dd = {dt_cols[0]: [s[0] for s in dt_data],
                  dt_cols[1]: [s[1] for s in dt_data]}

            dt_df = pd.DataFrame(dd)
            return dt_df

    def find_dt_code(self, dt_name: str) -> str:
        return self.dt_code_dict.get(dt_name, None)

    def find_dt_name(self, dt_code: str) -> str:
        return self.dt_name_dict.get(dt_code, None)



#  #############################################################


class BlsSmSid(BaseModel):
    prefix: str= Field(min_length=2, max_length=2)
    seas_adj: str = Field(min_length=1, max_length=1)
    state: str = Field(min_length=2, max_length=2)
    area: str = Field(min_length=5, max_length=5)
    super_ind: str = Field(min_length=8, max_length=8)
    data_type: str =Field(min_length=2, max_length=2)

    def to_sid(self):
        return ''.join([
            self.prefix.strip(),
            self.seas_adj.strip(),
            self.state.strip(),
            self.area.strip(),
            self.super_ind.strip(),
            self.data_type.strip(),
        ])


class ParseBlsSmSid:
    def __init__(self, sid='SMU19197802023800001'):
        self.prefix = sid[0:2]
        self.seas_adj = sid[2:3]
        self.state = sid[3:5]
        self.area = sid[5:10]
        self.super_ind = sid[10:18]
        self.data_type = sid[18:20]
        self.sid = sid

    @classmethod
    def get_industry_from_sid(cls, sid: str) -> str|None:
        return ParseBlsSmSid(sid).super_ind


    def get_industry_name(self):

        return IndustryData().find_industries_name(self.super_ind)
    def get_state_name(self):
        return StateData().find_state_name(self.state)

    def to_display_raw(self):

        return f'prefix: {self.prefix}\n seas. adj.: {self.seas_adj}\n state: {self.state}\n area: {self.area}\n super. ind.: {self.super_ind}\n data type: {self.data_type}'

    def to_display(self):
        prefix = self.prefix
        seas_adj = self.seas_adj
        state = StateData().find_state_name(self.state)
        ind_name = IndustryData().find_industries_name(self.super_ind)
        return f'{prefix} {seas_adj} {state} {ind_name} {self.data_type}'


class BuildBlsSmSid:
    def __init__(self, prefix:str, seas_adj:str, state:str, area:str, super_ind:str, data_type:str):
        self.prefix = prefix
        self.seas_adj = seas_adj
        self.state = state
        self.area = area
        self.super_ind = super_ind
        self.data_type = data_type

    def build(self):

        return BlsSmSid(prefix=self.prefix,
                        seas_adj=self.seas_adj,
                        state=self.state,
                        area=self.area,
                        super_ind=self.super_ind,
                        data_type=self.data_type)

series_lst = ['CUUR0000SA0', 'SUUR0000SA0']


class BlsStateEmpRequest:
    def __init__(self, seriesid: List[str], syear: str, eyear: str):
        self.headers = {'Content-type': 'application/json'}
        self.data = json.dumps({"seriesid": seriesid, "startyear": syear, "endyear": eyear})
        self.url = 'https://api.bls.gov/publicAPI/v1/timeseries/data/'

    def do_request(self) -> pd.DataFrame:
        p = requests.post(self.url, data=self.data, headers=self.headers)
        json_data = json.loads(p.text)
        x = pd.DataFrame(data=None,
                         index=None,
                         columns=["seriesid", "year", "period", "value", "footnotes"])
        for series in json_data['Results']['series']:

            seriesId = series['seriesID']
            for item in series['data']:
                year = item['year']
                period = item['period']
                value = item['value']
                footnotes = ""
                for footnote in item['footnotes']:
                    if footnote:
                        footnotes = footnotes + footnote['text'] + ','

                if 'M01' <= period <= 'M12':
                    new_row = pd.DataFrame([{
                        "seriesid": seriesId,
                        "year": year,
                        "period": period,
                        "value": value,
                        "footnotes": footnotes,
                    }])
                    x = pd.concat([x, new_row], ignore_index=True)
        return x


class SMQuery:
    def __init__(self, sid:list|BlsSmSid, state:str='54'):
        if type(sid)==list:
            self.sids:list[BlsSmSid] = sid
        elif type(sid)==BlsSmSid:
            self.sids:list[BlsSmSid] = [sid]
        else:
            raise ValueError(f"Invalid sid type: {type(sid)}")
        self.api_key = BLS_API_KEY

        self.state = state

        self.sample_series2 = 'SMS19000002023800001'
        self.sample_series3 = 'SMS19000002023800001'
        self.sample_series4 = 'SMS54000000000000001'
        self.single_queries = {'v1': f"https://api.bls.gov/publicAPI/v1/timeseries/data/{self.sample_series4}",
        'v2': f"https://api.bls.gov/publicAPI/v2/timeseries/data/{self.sample_series4}",
        'url_v2_data': f"?startyear=2024&endyear=2024&registrationkey={BLS_API_KEY}"}
        #
        # r = requests.get(url_v1)
        # print(r.json())
        #
        # simple_vi_res_json = r.json()
        # v2_resp = requests.get(url_v2)}


    @classmethod
    def chunked(cls, seq, size=10):
        return [seq[i:i+size] for i in range(0, len(seq), size)]

    @classmethod
    def sm_series_from_ind_id(cls, ind_ids:list, state='54')->SMQuery:
        series_ids:list[BlsSmSid] = []


        for code in ind_ids:
            dd = {}
            dd['prefix'] = 'SM'
            dd['seas_adj'] = 'S'
            dd['state'] = state
            dd['area'] = '00000'
            dd['ind_code'] = code
            dd['data_types'] = '01'
            series_ids.append(BlsSmSid(**dd))
        return SMQuery(series_ids, state)


# multiples with v2
        headers = {'Content-type': 'application/json'}

        data = json.dumps({"seriesid": series_ids,"startyear":startyear, "endyear":endyear,"registrationkey":api_key})
        p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        res_data = {}
        res_data['series'] = series_ids
        res_data['startyear'] = startyear
        res_data['endyear'] = endyear
        res_data['res'] = p.text
        return res_data



    @classmethod
    def BlsV2Batch(cls, chnks:list, syear:str='2015', endyear:str='2024', outf:str='blsquery_1_2.json'):
        import time
        api_key = BLS_API_KEY
        data_out_dir = Path('data\\bls_api\\bls_query_data\\')
        res_array = []
        for chnk in chnks:
            res = SMQuery.bls_v2_SM_multi_request(chnk, api_key, syear, endyear)
            res_array.append(res)
            time.sleep(30)
        with open(data_out_dir / outf, 'w') as outfile:
            json.dump(res_array, outfile)
        return res_array

class ValidateIndId:
    def __init__(self, industries: IndustryData, ind_id,state:str='West Virginia'):
        self.ddir = 'data\\bls_api\\bls_query_data\\'
        self.industries = industries
        self.prefix:str = 'SM'
        self.seas_adj: list[str] =['U', 'S']
        self.state:str = StateData().find_state_code(state)
        # print(f"state: {self.state}")
        self.area:str = AreaData().areas_code_dict.get('Statewide', None)
        # print(f"area: {self.area}")
        if self.area is None:
            raise ValueError(f"Invalid area code: {state}")
        self.super_ind:str = ind_id
        self.data_type:str = '01'
        self.sid_1: BlsSmSid = BuildBlsSmSid(self.prefix, self.seas_adj[0], self.state, self.area,self.super_ind, self.data_type).build()
        self.sid_2: BlsSmSid = BuildBlsSmSid(self.prefix, self.seas_adj[1], self.state, self.area,self.super_ind, self.data_type).build()
        self.ind_desc = self.industries.industries_code_dict['industry_name'].get(self.super_ind, None)
        if self.ind_desc is None:

            raise ValueError(f"Invalid industry desc: {self.super_ind}")
        self.obj_states =  ['TEST_SID', 'TEST_SID_REQ', 'EVAL_RESPONSE']
        self.obj_state =self.obj_states[0]



        # print(self.sid_1.to_sid())
        # print(self.sid_2.to_sid())
        # print(self.ind_desc)

    def change_state(self, new_state:int):
        self.obj_state = self.obj_states[new_state]

    def sids_to_json(self):
        dd = {'sid_1': self.sid_1.to_sid(), 'sid_2': self.sid_2.to_sid(), 'ind_desc': self.ind_desc}
        with open(self.ddir + 'sid_data_' + self.super_ind + '.json', 'w') as f:
            json.dump(dd, f)
        return dd





class ValidateRequest:
    def __init__(self, series_ids:list[BlsSmSid], ind_desc: str, state:str):
        self.series_ids = series_ids
        self.ind_desc = ind_desc
        self.state = state
        self.smq:SMQuery = SMQuery(self.series_ids, self.state )

    def do_request(self) -> dict:
        str_ids = [sid.to_sid() for sid in self.smq.series_ids]
        resp = self.smq.bls_v2_SM_multi_request(self.smq.series_ids,
                                               self.smq.api_key,
                                               startyear='2024',
                                               endyear='2024')
        return resp


class BuildSMResponse:
    def __init__(self, resp:dict):
        self.resp = resp
        self.res = resp['res']
        if type(self.res) is str:
            import json
            self.res = json.loads(self.res)
        self.ind_desc = self.resp['sid_desc']

        self.status = self.res['status']
        self.responseTime = self.res['responseTime']
        self.res_results = self.res['Results']
        self.results = BuildSMIdResults(self.res_results, self.ind_desc).build()
    def build(self):
        dd:dict = {'res':self.res,
                   'ind_desc':self.ind_desc,
                   'status': self.status,
                   'responseTime': self.responseTime,
                   'results': self.results}
        return SMResponse(**dd)


@dataclass
class SMResponse:
        res: dict
        ind_desc: str
        status: str
        responseTime: str
        results: SMIdResults


@dataclass
class SMIdResults:
    r_ids:list[dict]
    ind_desc:str
    score:str

    def to_dict(self):
        return {'r_ids': self.r_ids, 'ind_desc': self.ind_desc, 'score': self.score}


class BuildSMIdResults:
    def __init__(self, smid_results: dict, ind_desc: str):
        # print(f" results dict: {smid_results}")


        self.r_ids = []
        self.ind_desc = ind_desc
        self.results = smid_results['series']
        self.score = 0
        # print(f"BuildSMIdResults: len  results: {len(self.results)}, ind_desc: {self.ind_desc}")
        for s in self.results:
            ser_id = s['seriesID']
            data = s.get('data', None)

            if not data:
                self.score =  self.score + 0
            else:
                self.score = self.score + 1
            self.r_ids.append({'ser_id': ser_id, "data": data, "score": str(self.score)})


    def build(self):
        return SMIdResults(r_ids=self.r_ids, ind_desc=self.ind_desc, score=self.score)


class SMData:
    def __init__(self, results_obj:SMIdResults):
        rids = results_obj.r_ids
        self.results = [SMResult(rid) for rid in rids]
        self.ind_desc = results_obj.ind_desc
        self.score = results_obj.score

        def get_score(self):
            return self.score




class PeriodData:
    def __init__(self, pdata: dict):
        self.year = pdata['year']
        self.period = pdata['period']
        self.value = pdata['value']
        self.footnotes = pdata['footnotes']
        self.periodName = pdata['periodName']

    def to_dict(self):
        return self.__dict__


class SMResult:  # SMIdResults.results[0|1]
    def __init__(self, series_data: dict):

        # print(f"series: {series_data}")
        self.series = series_data['ser_id']
        self.series_data = [PeriodData(pd) for pd in series_data['data']]
    def get_seas_adj(self):
        if self.series.startswith('SMU'):
            return "U"
        elif self.series.startswith('SMS'):
            return "S"
        else:
            raise ValueError(f'unexpected seas_adj value in ser_id  {self.series}')

    def get_dataframe(self) -> pd.DataFrame:

        dd = [ppd.to_dict() for ppd in self.series_data]
        df = pd.DataFrame(dd)
        return df

    def get_ser_id(self):
        return self.series






















