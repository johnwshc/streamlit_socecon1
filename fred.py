import pandas as pd


from states_idx import dd
import plotly.express as px
import plotly.graph_objects as go


class FredMgr:
    median_income_data_fn = "data/fred/MEDIAN_HH_INCOME_BY_STATE_1984_2023.xlsx"
    hhmed_readme_fred_fn = "data/fred/hhmed_fred.json"
    def __init__(self):
        self.mgr = {}
        self.states_idx = dd
        self.df_readme = self.load_data_readme()
        self.df_me_ho_data = self.load_data()
        self.pop_data = self.load_pop_data()
        self.states_gdp_2025 = FredMgr.load_states_gdp_2025()
        self.states_gdp_pc = self.load_gdp_pc()

        self.state_dicts: list[dict] = []
        self.saved_state_me_ho_dicts: list[dict] = FredMgr.load_json_hhmed_data()

    def load_gdp_pc(self):
        df_gdp = self.states_gdp_2025
        df_pop = self.pop_data
        popdf = df_pop[['state_codes', '2025']].copy()
        popdf_idx = popdf.set_index('state_codes', drop=True)
        pop_dict = popdf_idx.to_dict()
        pd = pop_dict['2025']
        df_gdp['pop_2025'] = df_gdp['state_codes'].apply(lambda x: pd.get(x,0))
        df_gdp.columns = ["GeoName", "GDP_2025", "state_codes", "pop_2025"]
        df_gdp['gdp_per_capita'] = df_gdp.apply(lambda row: (row['GDP_2025'] * 1000000) / row['pop_2025'], axis=1)
        return df_gdp

    @classmethod
    def fix_gdp_state_code(cls, x):
        scode = dd.get(x,None)
        if not scode:
            return x
        return scode

    @classmethod
    def fix_pop_state_code(cls, x):
        scode = dd.get(x,None)
        if not scode:
            return x
        return scode


    @classmethod
    def load_data_readme(cls):
        return pd.read_excel(FredMgr.median_income_data_fn, sheet_name="README")

    @classmethod
    def load_states_gdp_2025(cls):

        states_gdp_fn = "data/fred/gdp_2025_states.csv"
        df_gdp = pd.read_csv(states_gdp_fn)
        df_gdp['state_codes'] = df_gdp['GeoName'].apply(FredMgr.fix_gdp_state_code)
        df_gdp.drop(columns=['GeoFIPS'], inplace=True)
        df_gdp.columns = ["GeoName", "2025 GDP (millions)", "state_codes"]
        df_gdp = df_gdp.iloc[1:52,].copy()
        return df_gdp




    @classmethod
    def load_data(cls):
        xdata_df = pd.read_excel(cls.median_income_data_fn, sheet_name="Annual")
        cols = xdata_df.columns
        alt_cols = [col[8:10] for col in cols]
        alt_cols[0] = 'date'
        xdata_df.columns = alt_cols
        xdata_df = xdata_df.iloc[41, :].copy()
        xdata_df = xdata_df.reset_index()
        xdata_df = xdata_df.iloc[1:]
        xdata_df.columns = ['state_codes', 'median income']
        xdata_df['median income'] = xdata_df['median income'].astype(int)
        return xdata_df


    def clean_fred_mgr_readme(self):
        # mgr = FredMgr()
        self.df_readme = self.df_readme.drop(columns=['Unnamed: 1', 'Unnamed: 2'])
        self.df_readme = self.df_readme.dropna()
        self.df_readme.reset_index(drop=True, inplace=True)
        self.dfr = self.df_readme.iloc[6:,]
        self.dfr.reset_index(drop=True, inplace=True)
        self.dfr.columns = ["data_list"]
        self.ser_r = self.dfr.data_list
        list_read: list[str] = self.ser_r.tolist()
        sid_count = 0
        idx = range(len(list_read))
        tdict = {}
        for i in idx:
            if i % 2 == 0:
                if list_read[i].startswith("Series ID"):
                    sid_count += 1
                    if sid_count > 1:
                        self.state_dicts.append(tdict)
                        tdict = {}
                    param = list_read[i]
                    value = list_read[i + 1]
                    tdict[param] = value
                else:
                    param = list_read[i]
                    value = list_read[i + 1]
                    tdict[param] = value
            else:
                continue

    def save_json(self):
        import json
        hhmed_readme_fred_fn = "data/fred/hhmed_fred.json"
        with open(hhmed_readme_fred_fn, "w") as f:
            json.dump(self.state_dicts, f)

    @classmethod
    def load_json_hhmed_data(cls):
        import json
        with open(cls.hhmed_readme_fred_fn) as f:
            hh_med_dicts = json.load(f)
        return hh_med_dicts

    def load_pop_data(self):
        import pandas as pd
        pop_fn = "data/fred/NST-EST2025-POP.xlsx"
        df_pop = pd.read_excel(pop_fn)
        df_pop.columns = ['geography', '4-1-2020', '2020', '2021', '2022', '2023', '2024', '2025']
        df_pop = df_pop.drop([0, 1, 2])
        df_pop.reset_index(drop=True, inplace=True)
        df_pop.dropna(inplace=True)
        df_pop.reset_index(drop=True, inplace=True)
        df_pop = df_pop.drop([0,1,2,3,4])
        df_pop.reset_index(drop=True, inplace=True)
        df_pop.drop(51, inplace=True)
        df_pop["geography"] = df_pop["geography"].apply(lambda x: x[1:] if x.startswith(".") else x)
        df_pop["state_codes"] =  df_pop["geography"].apply(FredMgr.fix_pop_state_code)
        return df_pop



class FredGraphs:
    def __init__(self, mgr: FredMgr):
        self.mgr = mgr

    def us_states_hhmed(self):
        dff = self.mgr.df_me_ho_data
        # print(f"{dff.state_codes.head()}")
        fig = px.choropleth(dff,
                            locations='state_codes',
                            locationmode="USA-states",
                            scope="usa",
                            color='median income',
                            color_continuous_scale="Viridis_r",

                            )
        fig.show()

    def states_gdp(self):
        dff = self.mgr.states_gdp_2025.iloc[1:,].copy(deep=True)
        dff.reset_index(drop=True, inplace=True)
        dff["2025 GDP (millions)"] = dff["2025 GDP (millions)"].round(2)
        dff["state_codes"] = dff["state_codes"].apply(lambda x: x.strip())
        fig = px.choropleth(dff,
                            locations='state_codes',
                            locationmode="USA-states",
                            scope="usa",
                            color="2025 GDP (millions)",
                            color_continuous_scale="Viridis_r",

                            )
        fig.show()


    def states_pop(self):
        df_pop = self.mgr.pop_data[['state_codes', '2025']]
        fig = px.choropleth(df_pop,
                            locations='state_codes',
                            locationmode="USA-states",
                            scope="usa",
                            color="2025",
                            color_continuous_scale="Viridis_r",

                            )
        fig.show()

    def states_gdp_pc(self):
        dff = self.mgr.states_gdp_pc
        dff.reset_index(drop=True, inplace=True)
        dff.drop(8,inplace=True)
        dff.reset_index(drop=True, inplace=True)
        fig = px.choropleth(dff,
                            locations='state_codes',
                            locationmode="USA-states",
                            scope="usa",
                            color="gdp_per_capita",
                            color_continuous_scale="Viridis_r",)
        fig.add_trace(
            go.Scattergeo(
                locationmode="USA-states",
                locations=dff["state_codes"],
                text=dff["gdp_per_capita"].round(2),
                mode="text",
                textfont=dict(
                    size=9,
                    color="black"
                ),
                showlegend=False
            )

        )
        fig.write_html("states_gdp_pc.html")

        fig.show()


