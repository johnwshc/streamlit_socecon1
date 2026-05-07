
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from emp_bundles import SAEmpGdpMgr as Mgr
from employees_2024 import EmpInd2024 as EmpInd
from parse_lncodes import LCMeta, LCIndex
from pathlib import Path


class GdpDisplays:

    def __init__(self, gmgr: Mgr):
        self.gmgr = gmgr
        self.sdf = gmgr.df_sagdp2.copy(deep=True)
        self.short_index: LCIndex = LCIndex.parse_codes(Path('data\\gdp_short_classes.txt').as_posix())
        long_index = LCIndex.parse_codes(Path('data\\gdp_classes.txt').as_posix())
        self.sdf['ShortDesc'] = self.sdf.LineCode.apply(self.short_index.get_desc)
        self.sdf.drop(['clean_description'], axis=1, inplace=True)
        self.sdf_r2 = self.gmgr.get_rank_2_ind2024()
        self.sdf_r2['short_desc'] = self.sdf_r2.LineCode.apply(gmgr.lc_short_index.get_desc)
        self.sdf_r2.drop(['clean_description'], axis=1, inplace=True)


    def show_nd_gdp_by_industry_category_2(self, state='North Dakota') -> px.bar:
        sorted_df = self.sdf_r2.sort_values(by='2024', ascending=False)

        fig = px.bar(
            sorted_df,
            x='short_desc',
            y='2024',
            color='category',
            category_orders={
                'category': ['service', 'production', 'public', 'agricultural'],
                'ShortDesc': list(sorted_df['short_desc'])
            },
            labels={
                '2024': '2024 N. Dakota GDP in millions',
                'short_desc': 'Public and Private Industries',
                'category': 'Category'
            },
            title=f'{state} GDP by Industry Category'
        )
        return fig

class EmpDisplays:
    def __init__(self, mgr: Mgr):
        self.ls_map: dict = EmpInd.emp_long_short_descs_map
        self.emp_df = mgr.edf_state_data.copy(deep=True)
        self.mgr = mgr
        emp_dff = self.emp_df.reset_index()
        emp_dff['short_desc'] = emp_dff.Description.apply(lambda x: self.ls_map.get(x, 'Unknown'))
        emp_dff.drop([0], inplace=True)
        emp_dff.reset_index(drop=True, inplace=True)
        emp_dff.rename(columns={f'{mgr.state_name}': '2024 employees (in thousands)'}, inplace=True)
        emp_dff.drop(['Description'], axis=1, inplace=True)
        self.emp_dff = emp_dff.copy(deep=True)
        print(f"emp_dff.head() {self.emp_dff.head()}")



    def show_emp_by_industry_category_2(self) -> px.bar:

        sorted_df = self.emp_dff.sort_values(by='2024 employees (in thousands)', ascending=False)
        state = self.mgr.state_name
        fig = px.bar(
            sorted_df,
            x='short_desc',
            y='2024 employees (in thousands)',
            color='category',
            category_orders={
                'category': ['service', 'production', 'public', 'agricultural'],
                'ShortDesc': list(sorted_df['short_desc'])
            },
            labels={
                '2024': f'2024 {state} Employment (in thousands)',
                'short_desc': 'Employment by Industry',
                # 'category': 'Category'
            },
            title=f'{state} Employment Industry Category'
        )
        return fig

class CompDisplays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()
        # self.short_index: LCIndex = LCIndex.parse_codes(Path('data\\gdp_short_classes.txt').as_posix())
        # long_index = LCIndex.parse_codes(Path('data\\gdp_classes.txt').as_posix())
        # self.df['ShortDesc'] = self.sdf.LineCode.apply(self.short_index.get_desc)
        # self.df.drop(['clean_description'], axis=1, inplace=True)
        # self.sdf_r2: pd.DataFrame = self.gmgr.get_rank_2_ind2024()
        # self.sdf_r2.reset_index(drop=True, inplace=True)


class TaxDisplays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()

class SurplusDisplays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()

class TaxSubsDisplays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()

class Subsidies_displays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()

class ReaGdpDisplays:
    def __init__(self, mgr: Mgr) -> pd.DataFrame:
        self.gmgr = mgr
        self.df = mgr.df_sagdp2.copy(deep=True)
        self.rdfs = mgr.get_rank_2_ind2024()








