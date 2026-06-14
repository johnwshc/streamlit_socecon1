
import plotly.express as px
from emp_bundles import SAEmpGdpMgr as Mgr
from employees_2024 import EmpInd2024 as EmpInd
import pandas as pd


class GdpDisplays:

    def __init__(self, mgr: Mgr):
        self.gmgr = mgr
        self.sdf_r2 = self.gmgr.get_rank_2_ind2024()
        self.sdf_r2['short_desc'] = self.sdf_r2.LineCode.apply(self.gmgr.lc_short_index.get_desc)
        self.sdf_r2.drop(['clean_description'], axis=1, inplace=True)
        self.state = self.gmgr.state_name


    def sa_gdp_by_industry_r2(self) -> px.bar:
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
                '2024': f'2024 {self.gmgr.label}',
                'short_desc': 'Public and Private Industries',
                'category': 'Category'
            },
            title=f'2024 {self.state} {self.gmgr.title}'
        )
        return fig
    def sagdp_totals_yrs(self) -> px.bar:
        data_yrs = ['1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004',
                    '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014',
                    '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
        all_data = self.gmgr.data_all_class
        all_data_attrs = all_data.get_attrs()
        all_yrs_total_nom_gdp = {k: d for k, d in all_data_attrs.items() if k in data_yrs}
        all_yrs_total_nom_gdp_ser = pd.Series(all_yrs_total_nom_gdp)
        data_nd = all_yrs_total_nom_gdp_ser
        data_nd_df = data_nd.reset_index(inplace=False)
        data_nd_df.columns = ['Year', 'Total_GDP']
        fig_tot = px.bar(data_nd_df,
                     x='Year',
                     y='Total_GDP',
                     title='Total North Dakota GDP by Year',
                     labels={'Total_GDP': 'Total GDP (in millions of USD)'}
                     )
        return fig_tot


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
        # print(f"emp_dff.head() {self.emp_dff.head()}")



    def emp_by_industry_r2(self) -> px.bar:

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






