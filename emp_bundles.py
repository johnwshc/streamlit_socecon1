import pandas as pd
from typing import List
from dataclasses import dataclass
from lcx_codes import LCodes
from trees import TreeNode, TNUtils
from config import Config
from data_config import DataConfig
from parse_lncodes import LCIndex
from employees_2024 import EmpInd2024 as EmpInd
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
class ERDataClass:
    def __init__(self, data_dict):
        for key, value in data_dict.items():
            setattr(self, key, value)
        self.description = data_dict['Description']

        self.unit = data_dict['Unit']

    def get_attr(self, attr_v):
        return self.__getattribute__(attr_v)

    def get_attrs(self):
        return vars(self)


class SAEmpGdpMgr:

    """A manager class for handling state employment and GDP data, including loading, processing, and displaying the data."""

    states_name_map = {'ND':'North Dakota' ,
                       'WV':'West Virginia',
                       'MN':'Minnesota'}


    # @classmethod
    # def get_state_gdp_data(cls, sa_name: str='ND', doc='GDP') -> pd.DataFrame:
    #     if sa_name not in DataConfig.registered_states.keys():
    #         raise ValueError(f"State {sa_name} not registered in EmpConfig.registered_states.")
    #     if sa_name == 'ND':
    #         fn = DataConfig.registered_states[f'{sa_name}'][f'{doc}']
    #
    #     df = pd.read_json(fn)
    #     df.drop([92, 93, 94, 95], axis=0, inplace=True)
    #     return df

    @classmethod
    def get_nd_state_emp_bundles(cls, sa_name: str='ND') -> tuple[List[StateEmpDataBundle], pd.DataFrame]:
        state_bundles_fn = DataConfig.registered_states['ALL']['EMP']
        nd_state_bundles: List[StateEmpDataBundle] = SAEmpGdpMgr.restore_bundles_from_json(state_bundles_fn)

        bundle_dfs = [b.Employee_data for b in nd_state_bundles]
        bun_df_cat = pd.concat(bundle_dfs, axis=1)
        return nd_state_bundles, bun_df_cat

    def __init__(self, sa_name='ND', doc='GDP'):

        self.lc_index: LCIndex = LCIndex.parse_codes()
        self.lc_short_index: LCIndex = LCIndex.parse_codes(fn='data/ND2/gdp_short_classes.txt')
        self.nd_state_bundles, self.nd_edf = SAEmpGdpMgr.get_nd_state_emp_bundles()

        self.nd_emp_lcs: List[int] = LCodes.emp_lcs
        self.df_sagdp2 = DataConfig.get_state_gdp_data(sa_name, doc)

        #  get total for all industries -- not employment
        if doc != 'EMP':
            all_total = self.df_sagdp2.iloc[0,:]
            all_total_d = all_total.to_dict()
            # print(f"all _gdp_data: {all_total_d}")
            self.data_all_class = ERDataClass(all_total_d)
        else:
            self.data_all_class = None

        # get all private industries
        private_industries = self.df_sagdp2.iloc[1,:]

        # self.df_sagdp2 = self.df_sagdp2.set_index('Description')
        # self.df_sagdp2 = self.df_sagdp2.sort_values(by=['LineCode', 'Description'], ascending=[True, True])
        self.df_sagdp2['rank'] = self.df_sagdp2['LineCode'].apply(self.lc_index.get_rank)
        self.df_sagdp2['rank'] = self.df_sagdp2['rank'].astype(int)
        self.df_sagdp2["clean_description"] = self.df_sagdp2["Description"]
        self.df_sagdp2["category"] = self.df_sagdp2["LineCode"].apply(SAEmpGdpMgr.set_category)
        self. l2_mask = self.df_sagdp2['rank'] == 2
        self.emp_ind_2024: EmpInd = EmpInd()
        self.edf = self.emp_ind_2024.combined_extended.copy(deep=True)
        self.state_name = SAEmpGdpMgr.states_name_map[sa_name]
        self.sa_name = sa_name
        self.doc_name = doc
        self.label = DataConfig.labels[doc]
        self.title = DataConfig.titles[doc]
        self.edf_state_data = self.edf.loc[self.state_name].copy()
        ser_data = self.edf_state_data.copy()
        edf_state_data:pd.DataFrame = ser_data.reset_index()
        edf_state_data.rename(columns={'index': 'Description'}, inplace=True)
        edf_state_data['category'] = edf_state_data['Description'].apply(self.emp_ind_2024.get_emp_category)
        self.edf_state_data = edf_state_data.set_index('Description')

    def get_rank_2_ind2024(self) -> pd.DataFrame:
        gov_lc_83_s = self.df_sagdp2.iloc[82,].copy(deep=True)


        dff_rank2 = self.df_sagdp2[self.l2_mask]
        dff_rank2 =  dff_rank2.reset_index(drop=True)
        disp_columns_1 = ['LineCode', 'Description', '2024', 'category', 'clean_description', 'rank']
        disp_gdp = dff_rank2[disp_columns_1].copy()
        disp_gdp.loc[len(disp_gdp)] = {
            "LineCode": 83,
            "Description": "Government and government enterprises",
            "2024": 8423.6,
            "category": "public",
            "clean_description": "Government",
            "rank": 1
        }
        dff_rank22 = disp_gdp.copy(deep=True)
        dff_rank22 = dff_rank22.reset_index(drop=True)
        dff_rank22.LineCode = dff_rank22["LineCode"].astype(int)
        dff_rank22['2024'] = pd.to_numeric(dff_rank22['2024'], errors='coerce')

        return dff_rank22


    def get_tree(self) -> TreeNode:


        codes: pd.DataFrame = self.df_sagdp2[['LineCode', 'rank']].copy()
        # dcodes: pd.DataFrame = self.df_sagdp2[['LineCode', 'Description', 'rank']].copy()



        root = TreeNode(data=-1, parent=None, lc=0)
        tree: TreeNode = TNUtils.build_tree(codes, root)
        tree = root
        return tree



    @staticmethod
    def set_category( lc: int) -> str:
        linecode = int(lc)
        if linecode in LCodes.prod_lcs:
            return 'production'
        elif linecode in LCodes.svcs_lcs:
            return 'services'
        elif linecode in LCodes.dist_lcs:
            return 'services'
        elif linecode in LCodes.ag_lcs:
            return 'agriculture'
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



    # def get_2024_classification_descs(self) -> pd.DataFrame:
    #
    #     dff_nd_2024_gdp = self.clean_nd_for_2024_display()
    #     ##  [['Description', 'ShortDesc']].copy()
    #     return dff_nd_2024_gdp

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

        for b in self.nd_state_bundles:
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


    # @classmethod
    # def get_short_desc(cls, lc: int):
    #     lines2: list[str] = []
    #     with open(fnn) as f:
    #         lines = f.readlines()
    #         for line in lines:
    #             # print("original line:", repr(line))
    #             line = line.strip()
    #             # print("stripped line:", repr(line))
    #             line = cls.strip_leading_number(line)
    #             # print("stripped leading number line:", repr(line))
    #             if line:
    #                 lines2.append(line)
    #     return pd.Series(lines2)




    @classmethod
    def restore_bundles_from_json(cls, jpath: str) -> List[StateEmpDataBundle]:
        import json
        with open(jpath, 'r') as f:
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

    @classmethod
    def get_state_data(cls) -> pd.DataFrame:
        return cls.load_df_from_json(cls.data_file)

    # @classmethod
    # def get_state_dcodes(cls) -> pd.DataFrame:
    #     return cls.load_dcodes_from_json(Config.SA_GDP_DCODES_ND)

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

