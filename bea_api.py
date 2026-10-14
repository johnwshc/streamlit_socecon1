
import requests
import pandas as pd
from dataclasses import dataclass

from numpy.random.mtrand import beta

from bls_api import IndustryData
from lcx_codes import LCodes
from parse_lncodes import LCIndex, LCMeta
from lcx_codes import LCodes

BEA_API_KEY = "B5772664-66EF-46AE-A4AB-142ED734A7D4"
# Your query parameters as key-value pairs
class BEA_META:

    BEA_API_KEY = "B5772664-66EF-46AE-A4AB-142ED734A7D4"
    BASE_URL = "http://apps.bea.gov/api/data"
    dataset_name = 'Regional'

    @classmethod
    def in_parts(cls):
        query_parameters = {
            'UserID': BEA_META.BEA_API_KEY,
            'method': 'GETDATASETLIST',
            'ResultFormat': 'JSON'
        }
        request_url = f"{BEA_META.BASE_URL}"
        response = requests.get(request_url, params=query_parameters)
        return response.json()

    @classmethod
    def BeaDatasets(cls):
        request_url = f"{BEA_META.BASE_URL}?&UserID={BEA_META.BEA_API_KEY}&method=GETDATASETLIST&ResultFormat=JSON"
        response = requests.get(request_url)
        rjson = response.json()
        results = rjson['BEAAPI']['Results']['Dataset']
        df_meta = pd.DataFrame(data=None, index=None, columns=['DatasetName', 'DatasetDescription'])
        for r in results:
            new_row = pd.DataFrame([{
                "DatasetName": r['DatasetName'],
                "DatasetDescription": r['DatasetDescription'],
            }])
            df_meta = pd.concat([df_meta, new_row], ignore_index=True)
        return df_meta

    @classmethod
    def get_dataset_parameters(cls):

        url = f'https://apps.bea.gov/api/data?&UserID={BEA_META.BEA_API_KEY}&method=getparameterlist&datasetname={BEA_META.dataset_name}&ResultFormat=JSON'
        response = requests.get(url)
        rjson = response.json()
        results = rjson['BEAAPI']['Results']['Parameter']

        return results

    @classmethod
    def get_line_codes(cls) ->pd.DataFrame:
        dataset = BEA_META.dataset_name
        method = 'GetParameterValuesFiltered'
        url = f'http://apps.bea.gov/api/data'
        qparams = {'UserID': BEA_META.BEA_API_KEY,
                   'method': method,
                   'datasetname': dataset,
                   'TargetParameter': 'LineCode',
                   'TableName': 'SAGDP2',
                   'ResultFormat': 'JSON'}
        response = requests.get(url=url, params=qparams)

        rjson = response.json()
        keys: list[dict] = rjson['BEAAPI']['Results']['ParamValue']
        lc_df = pd.DataFrame(data=None, index=None, columns=['LC', 'Description'])
        for k in keys:
            lc = k['Key']
            desc = k['Desc'].split(':', 1)[1]
            lc_df.loc[len(lc_df)] = [lc, desc]
        return lc_df

    @classmethod
    def TablesQuery(cls):
        url = BEA_META.BASE_URL
        qparams = {'UserID': BEA_META.BEA_API_KEY,
                   'method': 'GetParameterValues',
                   'datasetname': BEA_META.dataset_name,
                   'ParameterName': 'TableName',
                   'ResultFormat': 'JSON'}
        res = requests.get(url, params=qparams)
        return res.json()
        #  &UserID={BEA_META.BEA_API_KEY}&method=GetParameterValues&datasetname={dataset_name}&ParameterName=TableName&ResultFormat=JSON")


class BeaData:

    baseUrl = BEA_META.BASE_URL
    userid = BEA_META.BEA_API_KEY
    # GetData
    #  BEA_DATA(dataset='Regional', geofips='WV')
    def __init__(self,
                 dataset_name='Regional',
                 geofips='WV'):

        self.dataset_name = dataset_name
        self.userid = BeaData.userid
        self.geofips = geofips
        self.method = 'GetData'

    def get_regional_gdp_data(self, lc, table_name='sagdp2', years="LAST10"):
        print(f"get_regional_gdp_data for {lc} {table_name} {years}")
        qparams = {
            "UserID": self.userid,
            "method": self.method,
            "datasetname": self.dataset_name,
            "TableName": table_name,
            "LineCode": lc,
            "Year": years,
            "GeoFips": self.geofips,
            "ResultFormat": "JSON"
        }
        response = requests.get(self.baseUrl, params=qparams)
        return response.json()

@dataclass
class SDataNode:
    description:str
    table_name:str
    lc:str
    geofips:str
    year:str
    units:str
    value:str
    geoname:str

class BuildSDataNode:
    def __init__(self, d:dict):
        self.description = d['description']
        self.table_name = d['Code'].split('-', 1)[0]
        self.lc = d['Code'].split('-', 1)[1]
        self.geofips = d['GeoFips']
        self.year = d['TimePeriod']
        self.units = d['CL_UNIT']
        self.value = d['DataValue']
        self.geoname = d['GeoName']

    def build(self):
        return SDataNode(self.description, self.table_name, self.lc, self.geofips, self.year, self.units, self.value, self.geoname)

#      SATable, SATables, SADataCell, BeaRequest, SATableIndustry classes for parsing SAGDP data

class SATables:
    def __init__(self, data:dict):
        self.data:dict = data
        self.table_names = data.keys()
        self.tables:list[str] = []

class SADataCell:
    def __init__(self, cell_data:dict):
        self.cell_data = cell_data
        self.code = cell_data['Code']
        self.geo_fips = cell_data['GeoFips']
        self.geo_name = cell_data['GeoName']
        self.units = cell_data['CL_UNIT']
        self.year = cell_data['TimePeriod']
        self.data_value = cell_data['DataValue']

class BeaRequest:
    def __init__(self, data:dict):
        self.data = data
        # print(f"data in BEARequest: {data}")
        self.request_params = data['BEAAPI']['Request']['RequestParam']
        self.LineCode = self.get_request_param('LINECODE')['ParameterValue']
        self.GeoFips = self.get_request_param('GEOFIPS')['ParameterValue']
        self.Year = self.get_request_param('YEAR')['ParameterValue']
        # print(f"row top (BEAAPI) OF BEA Request: \n{self.data['BEAAPI']}")
        self.results = data['BEAAPI']['Results']


    def get_request_param(self, param_name:str):
        return next(p for p in self.request_params if p['ParameterName'] == param_name)

class SATableIndustry:
    def __init__(self, rdata:BeaRequest):
        self.request_data = rdata
        self.table_request_params = self.request_data.request_params
        self.LineCode = self.request_data.LineCode
        self.GeoFips = self.request_data.GeoFips
        self.results = rdata.results
        self.statistic = self.results['Statistic']
        self.units = self.results['UnitOfMeasure']
        self.table_description = self.results['PublicTable']
        self.years_data:list = self.results['Data']
        self.sa_data_cells: list[SADataCell] = []
        for ydata in self.years_data:
            sa_data_cell = SADataCell(ydata)
            self.sa_data_cells.append(sa_data_cell)



    # def get_request_params(self):
    #     params = self.request_data.request_params
    #     dparams = {p['ParameterName']:p['ParameterValue'] for p in params}
    #     return dparams

    def get_request_results(self):
        return self.request_data.results

class SATable:

    def __init__(self, tables:SATables, table_name:str):
        self.years = ['2015', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024','2024']
        self.sa_tables = tables
        self.data = self.sa_tables.data
        self.table_name = table_name
        self.df_table_fn = f"data/bea_api/{self.table_name}_table.json"
        self.sa_tables.tables.append(self.table_name)

        #  list of Table level  Requests -- BEAAPI objects encapsulating both request and results
        self.table_data: list = self.data[table_name]
        self.industries_data: list = []
        for tdata in self.table_data:
            beareq = BeaRequest(tdata)
            self.industries_data.append(SATableIndustry(beareq))
        self.df_table = self.get_df_table(self.industries_data)

    def get_df_table(self, industries_data) -> pd.DataFrame:
        dd = {'LC': [], 'Description': [], 'Units': [], '2015':[], '2016': [],
              '2017': [], '2018': [], '2019': [], '2020': [], '2021': [],
              '2022': [], '2023': [], '2024': []}
        for ind in industries_data:
            lc = ind.LineCode
            units = ind.units
            statistic = ind.statistic
            dd['LC'].append(lc)
            dd['Description'].append(ind.statistic)
            dd['Units'].append(units)
            cells = ind.sa_data_cells
            for cell in cells:
                year = cell.year
                value = cell.data_value
                dd[year].append(value)
        df_table = pd.DataFrame(dd)
        return df_table

    def save_df_table(self):
        filename = self.df_table_fn
        self.df_table.to_json(filename)

    @classmethod
    def load_df_table(cls, table_name:str):
        filename = f"data/bea_api/{table_name}_table.json"
        df_table = pd.read_json(filename)
        return df_table


class BeaMgr:

    def __init__(self, geofips='WV'):
        self.geofips = geofips
        self.bea_data = BeaData(geofips=self.geofips)
        self.bea_lc_df = BEA_META.get_line_codes()
        self.bls_industry_codes_de = IndustryData().industries_code_dict
        self.bls_industry_names_dd = IndustryData().industries_name_dict
        self.lc_orig_index = LCIndex.parse_codes()
        self.lcx_r2_codes = [str(lc.LineCode) for lc in self.lc_orig_index.lcx_codes if  lc.Rank == 2]
        self.short_codes = self.lcx_r2_codes[:3]
        self.other_lc_index_codes = LCodes
        self.gdp_table_names = ['sagdp2',
                                'sagdp3',
                                'sagdp4',
                                'sagdp5',
                                'sagdp6',
                                'sagdp7',
                                'sagdp8',
                                'sagdp9',
                                'sagdp1',
                                'sagdp11',]

        self.ryears = '2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024'

    def get_valid_table_linecodes(self, tname:str):
        key = BEA_META.BEA_API_KEY
        table_name = tname
        qparams = {'UserID': key,
                   'method': 'GetParameterValuesFiltered',
                   'datasetname': 'Regional',
                   'TargetParameter': 'LineCode',
                   'TableName': table_name,
                   'ResultFormat': 'JSON'}
        url = f"http://apps.bea.gov/api/data"
        # f"?&UserID={key}&method=GetParameterValuesFiltered&datasetname=Regional
        #       &TargetParameter=LineCode&TableName={table_name}&ResultFormat=JSON"
        res = requests.get(url, params=qparams)
        resj  = res.json()
        resj_results = resj['BEAAPI']['Results']['ParamValue']
        valid_sagdp2_lcs = [k['Key'] for k in resj_results]
        return valid_sagdp2_lcs

    def get_data(self, lcode, tablename='sagdp2'):
        str_years = '2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024'
        print(f"get_data for {lcode} {tablename} {self.ryears}")

        return self.bea_data.get_regional_gdp_data(lc=lcode, table_name=tablename, years=str_years)

    def get_lc_batch_data(self, lc_codes: list[str], tablename: str):
        import time

        batch_results = []

        for lc in lc_codes:
            print(f"\n******Getting data for {lc}\n")
            bea_data = self.get_data(lcode=lc, tablename=tablename)
            batch_results.append(bea_data)
            time.sleep(2)

        return batch_results

    def get_table_batch_data(self, tablenames: list[str], save=True, save_as: str = "JSON"):
        import time
        tables = {}
        # batch_results = []
        for tablename in tablenames:
            tbl_results = self.get_lc_batch_data(lc_codes=self.lcx_r2_codes, tablename=tablename)
            time.sleep(2)
            tables[tablename] = tbl_results
        if save:
            self.save_data(tables, save_as)
        return tables

    def save_data(self, data: dict, save_as: str = "JSON"):
        import json
        if save_as == "JSON":
            with open(f"data/bea_api/sagdp_{self.geofips}_tables_data.json", "w") as f:
                json.dump(data, f)
        else:
            raise ValueError(f"Unsupported save_as format. Use 'JSON': {save_as}")

    def load_tables_data(self):
        import json
        state = self.geofips
        with open(f"data/bea_api/sagdp_{state}_tables_data.json", "r") as f:
            data = json.load(f)
        return data

