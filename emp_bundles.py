import pandas as pd
from typing import List, Tuple, Optional
from dataclasses import dataclass
from lcx_codes import LCodes
from trees import TreeNode, TNUtils
from config import Config
import re



@dataclass()
class StateEmpDataBundle:
    """A data bundle for a specific state employment line code, containing metadata and the associated employee data."""
    Path:str
    LineCode:int
    Description:str
    Indent:int
    Employee_data: pd.DataFrame
    Units: str

    def to_json(self) -> dict:
        emp_data_json = self.Employee_data.reset_index().to_dict(orient='records')
        json_dict = {'LineCode': self.LineCode,
                     'Indent': self.Indent,
                     'Path': self.Path,
                     'Units': self.Units,
                     'Description': self.Description,
                     'Employee_data': emp_data_json}

        return json_dict

    @classmethod
    def from_json(cls, json_dict: dict) -> 'StateEmpDataBundle':
        """Extract a bundle object from a JSON file containing the bundle data."""
        emp_data_df = pd.DataFrame(json_dict['Employee_data']).set_index('Year')
        return StateEmpDataBundle(
            Path=json_dict['Path'],
            LineCode=json_dict['LineCode'],
            Description=json_dict['Description'],
            Indent=json_dict['Indent'],
            Employee_data=emp_data_df,
            Units=json_dict['Units']
        )


class EmpConfig:   #  needs to include data type (GDP, Surplus, Taxation, compensation, subsidies).
    """A configuration class for managing the specific US state (SA) associated with this data."""
    registered_states = {'ND':
                             {'name': 'North Dakota Employment Data 2015-2025',
                              'src': 'json/bundle.json'},
                         }
    # Placeholder for actual data, replace with real data as needed

class SAEmpGdpMgr:

    """A manager class for handling South Dakota employment and GDP data, including loading, processing, and displaying the data."""

    json_path: str = 'json\\bundle.json'
    json_gdp_path: str = 'json\\sa_gdp_df_nd.json'

    @classmethod
    def get_state_gdp_data(cls) -> pd.DataFrame:
        import json
        with open(cls.json_gdp_path, 'r') as f:
            df_json = json.load(f)
        df = pd.DataFrame(df_json).set_index('index')
        return df

    def __init__(self, conf:dict = None, bundles: List[StateEmpDataBundle] = None):
        self.conf = conf if conf is not None else EmpConfig.registered_states.get('ND')
        if bundles is None:
            self.state_bundles: List[StateEmpDataBundle] = SAEmpGdpMgr.restore_bundles_from_json(SAEmpGdpMgr.json_path)
        else:
            self.state_bundles: List[StateEmpDataBundle] = bundles
        self.emp_lcs: List[int] = LCodes.emp_lcs
        self.lcx_2_desc = {b.LineCode: b.Description for b in self.state_bundles}

        self.df_nd_gdp = SAEmpGdpMgr.get_state_gdp_data()
        self.indent = self.df_nd_gdp["Description"].str.extract(r'^( *)')[0].str.len()
        # if dtype == 'sagdp11':
        #     indent2 = self.indent.iloc[1:].copy()
        #     indent3 = indent2 / 2
        #     indent3 = indent3.astype(int)
        #     self.indent = indent3

        self.df_nd_gdp['indent'] = self.indent.astype(int)
        self.df_nd_gdp["clean_description"] = self.df_nd_gdp["Description"]
        self.df_nd_gdp["category"] = self.df_nd_gdp["LineCode"].apply(self.set_category)
        gov_lc_83_s = self.df_nd_gdp.iloc[82,].copy(deep=True)

        l2_mask = self.df_nd_gdp.indent == 2
        dff_rank2 = self.df_nd_gdp[l2_mask].copy(deep=True)
        dff_rank2 =  dff_rank2.reset_index(drop=True)
        disp_columns_1 = ['LineCode', 'Description', '2024', 'category', 'clean_description', 'indent']
        disp_gdp = dff_rank2[disp_columns_1].copy()
        disp_gdp.loc[len(disp_gdp)] = {
            "LineCode": 83,
            "Description": "Government and government enterprises",
            "2024": 8423.6,
            "category": "public",
            "clean_description": "Government",
            "indent": 1
        }
        self.dff_rank2 = disp_gdp.copy(deep=True)
        self.dff_rank2 = self.dff_rank2.reset_index(drop=True)
        self.dff_rank2.LineCode = self.dff_rank2["LineCode"].astype(int)
        self.dff_rank2['2024'] = pd.to_numeric(self.dff_rank2['2024'], errors='coerce')




        # # desc = self.df.Description.apply(str)
        # # print('desc\n', desc.head())
        # # print('indent', self.df['indent'].head())
        self.codes: pd.DataFrame = self.df_nd_gdp[['LineCode', 'indent']].copy()
        self.dcodes: pd.DataFrame = self.df_nd_gdp[['LineCode', 'Description', 'indent']].copy()



        self.root = TreeNode(data=-1, parent=None, lc=0)
        self.tree: TreeNode = TNUtils.build_tree(self.codes, self.root)
        self.tree = self.root


    #     build edf: concatenate employee_data in bundles
        edffs = [bundle.Employee_data for bundle in self.state_bundles]
        self.edf = pd.concat(edffs, axis=1)

    def extract_2024_state_emp_data(self) -> pd.DataFrame :
        row2024_emp = self.edf.loc[2024].copy()
        #  promote series to a dataframe.
        df_from_series = row2024_emp.reset_index()
        #  assign LineCode column
        df_from_series['LineCode'] = df_from_series['index'].apply(lambda x: SAEmpGdpMgr.get_lc(x, self.state_bundles))
        sdf_lcs = list(self.dff_rank2.LineCode)
        df_from_series['in_sdf'] = df_from_series.LineCode.apply(lambda x: True if x in sdf_lcs else False)
        return df_from_series

    def merge_2024_ind_emp(self) -> pd.DataFrame:

        enp_ddf = self.extract_2024_state_emp_data()
        mask = enp_ddf['in_sdf'] == True
        return enp_ddf[mask].copy().reset_index(drop=True)





    # def clean_nd_for_2024_display(self):
    #     """clean gdp data for a particular year, state, LineCodes, Unit type, and Description"""
    #
    #     df = self.df_nd_gdp.copy(deep=True)
    #     fn = f"{Config.DATA_DIR}/gdp_short_classes.txt"
    #
    #     lns = SAEmpGdpMgr.get_short_desc(fn)
    #     dff = df[['LineCode', 'Description', 'Unit', '2024', 'category']].copy()
    #     dff['2024'] = pd.to_numeric(dff['2024'], errors='coerce')
    #
    #     dff['indent'] = df['indent'].copy(deep=True)
    #     dff['ShortDesc'] = lns.copy(deep=True)
    #
    #
    #     return dff



    # %%
    def set_category(self, lc: int) -> str:
        linecode = int(lc)
        if linecode in LCodes.prod_lcs:
            return 'production'
        elif linecode in LCodes.svcs_lcs:
            return 'services'
        elif linecode in LCodes.dist_lcs:
            return 'distribution'
        elif linecode in LCodes.info_lcs:
            return 'information'
        elif linecode in LCodes.public_lcs:
            return 'public'
        elif linecode in LCodes.summary_lcs:
            return 'summary'
        else:
            return 'other'

    # helper bundle methods

    @classmethod
    def get_bundle(cls, lc, bundles:list) -> StateEmpDataBundle | None:
        for b in bundles:
            if b.LineCode == lc:
                print('Yes')
                return b
        else:
            return None

    @classmethod
    def get_lc(cls, desc, bundles):
        for b in bundles:
            if b.Description == desc:
                return b.LineCode
        else:
            return None

    @classmethod
    def get_desc(cls, lc, bundles):
        for b in bundles:
            if b.LineCode == lc:
                return b.Description
        else:
            return None

    def get_2024_classification_descs(self) -> pd.DataFrame:

        dff_nd_2024_gdp = self.clean_nd_for_2024_display()
        ##  [['Description', 'ShortDesc']].copy()
        return dff_nd_2024_gdp

    @classmethod
    def show_descs_table(cls, dff_classes: pd.DataFrame, title: str = 'Classification Descriptions',
                         col_labels: list | None = None) -> None:
        import plotly.graph_objects as go

        # If no custom labels provided, use the dataframe column names
        header_vals = col_labels if col_labels is not None else list(dff_classes.columns)

        # Build cell values in the same column order as the dataframe so header labels line up
        cells_vals = [dff_classes[col] for col in dff_classes.columns]

        fig2 = go.Figure(data=[go.Table(
            header=dict(values=header_vals,
                        fill_color='blue',
                        align='left'),
            cells=dict(values=cells_vals,
                       fill_color='gray',
                       align='left'))
        ])

        # Set title and layout options here
        fig2.update_layout(title_text=title, title_x=0.5, margin=dict(t=40, l=10, r=10))
        fig2.show()

    # clabels = ['Full Description', 'Short Description']
    # show_descs_table(dff_classifications, title='Classification Descriptions', col_labels=clabels)

    def build_lcx_dfs(self) -> dict:

        new_emp_inds = {}

        for b in self.state_bundles:
            ind_desc: str = b.Description
            ind_lc = b.LineCode
            units = b.Units
            data = b.Employee_data
            data.columns = [ind_desc]
            # data['Units'] = pd.Series([units] * len(data), index=data.index)
            new_emp_inds[ind_lc] = data
        return new_emp_inds

    #
    @classmethod
    def strip_leading_number(cls,line: str) -> str:
        return re.sub(r'^\s*\d+[\.\)]?\s+', '', line.rstrip('\n'))


    @classmethod
    def get_short_desc(cls, fnn: str):
        lines2: list[str] = []
        with open(fnn) as f:
            lines = f.readlines()
            for line in lines:
                # print("original line:", repr(line))
                line = line.strip()
                # print("stripped line:", repr(line))
                line = cls.strip_leading_number(line)
                # print("stripped leading number line:", repr(line))
                if line:
                    lines2.append(line)
        return pd.Series(lines2)




    @classmethod
    def restore_bundles_from_json(cls, json_path: str) -> List[StateEmpDataBundle]:
        import json
        with open(json_path, 'r') as f:
            blist = json.load(f)
        bundles = []
        for bdict in blist:
            bundle = StateEmpDataBundle.from_json(bdict)
            bundles.append(bundle)
        return bundles

    @classmethod
    def bundles_to_json(cls, bundles: List[StateEmpDataBundle]) -> None:
        import json
        blist = []
        for b in bundles:
            blist.append(b.to_json())
        with open('json\\bundle.json', 'w') as f:
            json.dump(blist, f, indent=4)
        print(f"Saved {len(blist)} bundles to json\\bundle.json")



    data_file = Config.SA_GDP_DF_ND

    @classmethod
    def get_state_data(cls) -> pd.DataFrame:
        return cls.load_df_from_json(cls.data_file)

    @classmethod
    def get_state_dcodes(cls) -> pd.DataFrame:
        return cls.load_dcodes_from_json(Config.SA_GDP_DCODES_ND)

    @classmethod
    def save_dcodes_to_json(cls, df: pd.DataFrame, json_path: str):
        import json
        if json_path is None:
            json_path = f"{Config.basedir}/json/sagdp_dcodes.json"
        df_json = df.reset_index().to_dict(orient='records')
        with open(json_path, 'w') as f:
            json.dump(df_json, f, indent=4)

    @classmethod
    def load_dcodes_from_json(cls, json_path: str) -> pd.DataFrame:
        import json
        with open(json_path, 'r') as f:
            df_json = json.load(f)
        df = pd.DataFrame(df_json).set_index('index')
        return df

    @classmethod
    def save_df_to_json(cls, df: pd.DataFrame, json_path: str):
        import json
        if json_path is None:
            json_path = f"{Config.basedir}/json/sa_gdp_df.json"
        df_json = df.reset_index().to_dict(orient='records')
        with open(json_path, 'w') as f:
            json.dump(df_json, f, indent=4)

    @classmethod
    def load_df_from_json(cls, json_path: str) -> pd.DataFrame:
        import json
        with open(json_path, 'r') as f:
            df_json = json.load(f)
        df = pd.DataFrame(df_json).set_index('index')
        return df

