import pandas as pd

class EmpInd2024:
    """A class to build a single dataframe indexed by state for 12 different broad
    categories of employment, published by the BLS in 4 separate stylesheets.  """
    sources = {
        'Bureau of Labor Statistics': 'https://www.bls.gov/sae/tables/state-news-release/home.htm',
    }
    year = 2024
    lc_emp2024_map = {
        'Total':[2-92],
        'Mining and logging': [6,7,8,9],
        'Construction': [11],
        'Manufacturing': [12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
        'Trade, transportation, and utilities': [10,34, 35,36,37,38,39,40,41,42,43,44],
        'Information': [45, 46,47,48,49],
        'Financial activities': [50,51,52,53,54,55,56,57,58],
        'Professional and business services': [59,60,61,62,63,64,65,66,67],
        'Education and health services': [68,69,70,71,72,73,74],
        'Leisure and hospitality': [75,76,77,78,79,80,81],
        'Other services': [82],
        'Government': [83,84,85,86]
    }
    emp_long_short_descs_map = {
        'Total': 'Total',
        'Mining and logging': 'Mining',
        'Construction': 'Construction',
        'Manufacturing': 'Mfg.',
        'Trade, transportation, and utilities': 'Trade/Utils.',
        'Information': 'Info.',
        'Financial activities': 'Fin./Rents',
        'Professional and business services': 'Biz Services',
        'Education and health services': 'Ed./Health',
        'Leisure and hospitality': 'Leisure',
        'Other services': 'Other',
        'Government': 'Govt.',
    }
    category_emp_map = {
        'Mining and logging': 'Production',
        'Construction': 'Production',
        'Manufacturing': 'Production',
        'Trade, transportation, and utilities': 'Services',
        'Information': 'Information',
        'Financial activities': 'Services',
        'Professional and business services': 'Services',
        'Education and health services': 'Services',
        'Leisure and hospitality': 'Services',
        'Other services': 'Services',
        'Government': 'Government',
    }
    def __init__(self):
        # d table compose
        self.default_units  = 'Thousands of employees'
        self.emp_doc_d1 = 'data/emp_doc2.xlsx'
        #
        # a,b,c tables compose
        self.emp_doc_a = "data/emp_doc_a.xlsx"
        self.emp_doc_b = "data/emp_doc_b.xlsx"
        self.emp_doc_c = "data/emp_doc_c.xlsx"
        self.dff_a = pd.read_excel(self.emp_doc_a, engine='openpyxl')
        self.dff_b = pd.read_excel(self.emp_doc_b, engine='openpyxl')
        self.dff_c = pd.read_excel(self.emp_doc_c, engine='openpyxl')
        self.combined_extended = self.get_combined_extended()




    def get_emp_data_d1(self) -> pd.DataFrame:
        dff_d = pd.read_excel(self.emp_doc_d1, engine='openpyxl')
        good_colsd = ['State', 'Leisure and hospitality', 'Other services','Government']
        dff_d1 = dff_d[good_colsd].copy(deep=True)
        dff_d1.reset_index(drop=True, inplace=True)
        drop_rows_1 = [7, 13]
        dff_d1.drop(drop_rows_1, axis=0, inplace=True)
        dff_d1.reset_index(drop=True, inplace=True)
        return dff_d1

    def get_emp_data_d2(self) -> pd.DataFrame:
        emp_doc_d2 = "data/emp_doc33.xlsx"
        dff_d2 = pd.read_excel(emp_doc_d2, engine='openpyxl')
        good_cols = ['State', 'Leisure and hospitality', 'Other services','Government']
        dff_d2 = dff_d2[good_cols].copy(deep=True)
        dff_d2.reset_index(drop=True, inplace=True)
        drop_rows = [0,1,6,12,18,24, 30,36,42,49]
        dff_d2.drop(drop_rows, axis=0, inplace=True)
        dff_d2.reset_index(drop=True, inplace=True)
        return dff_d2

    def get_combined_emp_data_d (self) -> pd.DataFrame:
        dff_d1 = self.get_emp_data_d1()
        dff_d2 = self.get_emp_data_d2()
        combined = pd.concat(
            [dff_d1.set_index("State"), dff_d2.set_index("State")],
            axis=0
        ).sort_index()
        combined = combined.reset_index()
        combined.drop([39,52,53], axis=0, inplace=True)
        combined.set_index("State", inplace=True)
        combined = combined.apply(pd.to_numeric, errors="coerce").astype(float)
        return combined

    def clean_dff_a(self) -> pd.DataFrame:

        df_a = self.dff_a.iloc[0:67,].copy(deep=True)

        df_a.reset_index(drop=True, inplace=True)
        top = df_a.iloc[0:35,].copy(deep=True)
        good_cols = ['State', 'Total', 'Mining and logging', 'Construction']
        top = top[good_cols].copy(deep=True)
        top = top.iloc[2:33,].copy(deep=True)
        top.reset_index(drop=True, inplace=True)
        bot = df_a.iloc[35:67,].copy(deep=True)
        bot.reset_index(drop=True, inplace=True)
        bot.columns = bot.iloc[0]
        bot.reset_index(drop=True, inplace=True)
        bot = bot[good_cols].copy(deep=True)
        bot = bot.iloc[3:,]
        bot.reset_index(drop=True, inplace=True)
        all_a =  pd.concat([top.set_index("State"), bot.set_index("State")],  axis=0)
        all_a.rename(index={'Delaware(1)':'Delaware',
                           'District of Columbia(1)':'District of Columbia',
                           'Hawaii(1)':'Hawaii',
                           }, inplace=True)
        all_a = all_a.mask(all_a == "-", 0.0).astype(float)
        all_a = all_a.apply(pd.to_numeric, errors="coerce").astype(float)
        return all_a



    # build table b

    def clean_dff_b(self) -> pd.DataFrame|pd.Series[float]:

        self.dff_b.columns = self.dff_b.iloc[0]
        self.dff_b.reset_index(drop=True, inplace=True)
        good_cols_b = ['State', 'Manufacturing', 'Trade, transportation, and utilities', 'Information']
        dfb = self.dff_b[good_cols_b].copy(deep=True)
        dfb = dfb.iloc[3:68,].copy(deep=True)
        dfb.drop([8,14, 15,16,17, 18,19, 25, 31, 37, 43,49, 55, 61 ], axis=0, inplace=True)
        dfb.reset_index(drop=True, inplace=True)
        dfb.set_index("State", inplace=True)
        dfb= dfb.apply(pd.to_numeric, errors="coerce").astype(float)
        return dfb



    def clean_dff_c(self) -> pd.DataFrame|pd.Series[float]:

        self.dff_c.columns = self.dff_c.iloc[0]
        good_columns_c = ['State', 'Financial activities', 'Professional and business services',
                          'Education and health services']
        dfc = self.dff_c[good_columns_c].copy(deep=True)
        dfc = dfc.iloc[3:68,].copy(deep=True)
        dfc.drop([8, 14, 20, 26, 32, 38, 40, 41, 42, 43, 44, 49, 55, 61], axis=0, inplace=True)
        dfc.reset_index(drop=True, inplace=True)
        dfc.set_index("State", inplace=True)
        dfc= dfc.apply(pd.to_numeric, errors="coerce").astype(float)
        return dfc

    def get_combined_extended(self,save=True) -> pd.DataFrame:

        all_states_a = self.clean_dff_a()
        all_states_b = self.clean_dff_b()
        all_states_c = self.clean_dff_c()
        all_states_d = self.get_combined_emp_data_d()


        combined_extended = pd.concat([all_states_a, all_states_b, all_states_c, all_states_d], axis=1)
        return combined_extended

    def get_emp_category(self, desc: str) -> str:
        return self.category_emp_map.get(desc, 'Other')

