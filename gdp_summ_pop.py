import pandas as pd
from config import Config
import plotly.graph_objects as go
import dataclasses
from typing import List

@dataclasses.dataclass
class StPop:
    state: str
    abbreviation: str
    year: int
    population: int

@dataclasses.dataclass
class StPopCollection:
    populations: list[StPop]


    def find_years(self, yrs: list[int]) -> list[StPop]:
        results = []
        for pop in self.populations:
            if pop.year in yrs:
                results.append(pop)
        return results

    def find_states(self, states: list[str]) -> list[StPop]:
        results = []
        for abbrev in states:
            for pop in self.populations:
                if pop.abbreviation == abbrev:
                    results.append(pop)
        return results


    def find_state_years(self, abbrev: str, years: list) -> List[StPop]|None:
        state = abbrev
        colls = []
        for year in years:
            for pop in self.populations:
                if pop.abbreviation == state and pop.year == year:
                    colls.append(pop)
        if len(colls) > 0:
            return colls
        else:
            return None




class Population:

    active_states = {"ND": "North Dakota",
                     "ME": "Maine",
                     "TX": "Texas",
                     "MN": "Minnesota",
                     "US": "United States",
                     "WV": "West Virginia"
                     }

    all_states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC',
                  'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN',
                  'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN',
                  'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ',
                  'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
                  'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA',
                  'WI', 'WV', 'WY']

    def __init__(self, load_existing=True):
        # self.state = state
        # self.year = year
        self.data_dir = Config.POP_DATA_DIR
        self.fn = f"{self.data_dir}/historical_state_population_by_year.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        self.df = self.clean(self.raw_df)
        # self.df: pd.DataFrame = self.clean(self.raw_df)
        if load_existing:
            self.active_states: StPopCollection = Population.load_populations()
        else:
            self.active_states: StPopCollection = self.build_state_pop_collection()

    def build_state_pop_collection(self, store=True) -> StPopCollection:
        populations = []
        for _, row in self.df.iterrows():
            state_abbr = row['State']
            if state_abbr in self.active_states.keys():
                state_name = self.active_states[state_abbr]
                year = int(row['Year'])
                population = int(row['Population'])
                st_pop = StPop(state=state_name,
                               abbreviation=state_abbr,
                               year=year,
                               population=population)
                populations.append(st_pop)
        st_pop_collection = StPopCollection(populations=populations)
        if store:
            self.store_populations(st_pop_collection)
        return st_pop_collection

    @classmethod
    def store_populations(cls, pops: StPopCollection) -> None:
        import json
        fn = f"{Config.POP_DATA_DIR}/state_populations.json"
        with open(fn, 'w') as f:
            json.dump(pops.model_dump(), f, indent=4)


    @staticmethod
    def load_populations() -> StPopCollection:
        import json
        fn = f"{Config.POP_DATA_DIR}/state_populations.json"
        with open(fn, 'r') as f:
            data = json.load(f)
            pops = StPopCollection.model_validate(data)
        return pops


    @classmethod
    def frep(cls, x):
            if ',' in x:
                return x.replace(",", "")
            else:
                return x

    def clean(self, ddf: pd.DataFrame) -> pd.DataFrame:
        ddf.columns = ["State", "Year", "Population"]
        ddf.Population = pd.to_numeric(ddf.Population).astype(int)
        ddf.Year = pd.to_numeric(ddf.Year).astype(int)
        return ddf


    def getPopulation(self, state: str, year: int) -> int:
        if state.lower() == "nd" or state.lower() == "north dakota":

            pop = int(self.df.loc[year, "Population"])
            return pop
        else:
            raise ValueError("Population data is only available for North Dakota.")





class GDPSummaryTable:
    default_state = "U.S."
    default_start_year = 2008
    default_end_year = 2024

    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.summary_dir = f"{self.data_dir}/gdp/SASUMMARY"
        self.good_colls = ['GeoFIPS', 'GeoName', 'Region', 'TableName', 'LineCode', 'Description',
                     'Unit', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008',
                     '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020',
                     '2021', '2022', '2023', '2024']

    def sclean(self, raw_dff: pd.DataFrame, is_all=False) -> dict:
        # remove non-data rows
        if is_all:
            dff = raw_dff.iloc[:780, ].copy()
        else:
            dff = raw_dff.iloc[:,: ].copy()
        dff = dff[self.good_colls]
        # remove all separate state rows
        df = dff.iloc[:15, :].copy(deep=True)
        # retain meta data rows
        df_meta = dff.iloc[781:, :].copy(deep=True)
        data = {'df': df, 'meta_df': df_meta}
        return data


    @staticmethod
    def build_summ_bar_chart(yrs, vals, units, title, **kwargs) -> go.Figure:
        dtype = kwargs.get('dtype', 'int')
        years = [str(year) for year in yrs]
        print('type of vals: ', dtype)
        # print(years)
        gdp_values = vals
        if dtype == 'int':
            gdp_numeric = pd.to_numeric(gdp_values, errors='coerce').round().astype(int)
        else:  # float
            gdp_numeric = pd.to_numeric(gdp_values, errors='coerce').round(2).astype(float)

        text_labels = [f"{v:,}" for v in gdp_numeric]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=years,
                    y=gdp_numeric,
                    text=text_labels,
                    textposition='auto',
                    textfont=dict(color='white'),
                    marker=dict(
                        color='#00bfff',  # bright/cyan bars
                        line=dict(color='rgba(255,255,255,0.12)', width=0.6)
                    )
                )
            ]
        )

        fig.update_layout(
            title=title,
            template='plotly_dark',
            paper_bgcolor='#0d1117',  # page background
            plot_bgcolor='#0d1117',  # plotting area background
            font=dict(color='white', family='Arial'),
            xaxis=dict(
                title='Year',
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.03)',
                zerolinecolor='rgba(255,255,255,0.06)'
            ),
            yaxis=dict(
                title=units,
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.03)',
                zerolinecolor='rgba(255,255,255,0.06)',
                tickformat=","
            ),
            margin=dict(t=64, b=40, l=64, r=24)
        )
        fig.data[0].update(textfont=dict(color='darkred'))
        return fig


    @staticmethod
    def display_real_gdp_barchart(df: pd.DataFrame,
                                  st=default_state,
                                  dtype="int",
                                  start=default_start_year,
                                  end=default_end_year) -> go.Figure:
        years = [str(year) for year in range(start, end)]
        title = f'{st} Annual Real GDP ({years[0]} - {years[-1]})'
        real_gdp: pd.Series = df.iloc[0,].copy(deep=True)
        units = real_gdp['Unit']
        gdp_values =  real_gdp[years].copy(deep=True).values
        fig = GDPSummaryTable.build_summ_bar_chart(years, gdp_values, units, title, dtype=dtype)
        return fig



    @staticmethod
    def display_real_all_income_barchart(df: pd.DataFrame,
                                         st=default_state,
                                         dtype='float',
                                         start=default_start_year,
                                         end=default_end_year) -> go.Figure:

        years = [str(year) for year in range(start, end)]
        title = f'{st} Annual Real Income ({years[0]} - {years[-1]})'
        real_income: pd.Series = df.iloc[1,].copy(deep=True)
        units = real_income['Unit']
        income_values = list(real_income[years].copy())
        fig: go.Figure = GDPSummaryTable.build_summ_bar_chart(years, income_values, units, title, dtype=dtype)
        return fig

    @staticmethod
    def display_real_all_per_capita_income_barchart(df: pd.DataFrame,
                                                    st=default_state,
                                                    dtype='int',
                                                    start=default_start_year,
                                                    end=default_end_year) -> go.Figure:

        years = [str(year) for year in range(start, end)]
        title = f'{st} Annual Real Per Capita Income ({years[0]} - {years[-1]})'
        real_per_capita_income: pd.Series = df.iloc[7,].copy(deep=True)
        units = real_per_capita_income['Unit']
        per_capita_income_values = list(real_per_capita_income[years].copy())
        fig: go.Figure = GDPSummaryTable.build_summ_bar_chart(years, per_capita_income_values, units, title, dtype=dtype)
        return fig

    @staticmethod
    def display_total_employment_barchart(df: pd.DataFrame,
                                          st=default_state,
                                          dtype="int",
                                          start=default_start_year,
                                          end=default_end_year) -> go.Figure:

        years = [str(year) for  year in range(start, end)]
        title = f'{st} Annual Total Employment ({years[0]} - {years[-1]})'
        total_employment: pd.Series = df.iloc[14,].copy(deep=True)
        units = total_employment['Unit']
        employment_values = list(total_employment[years].copy())
        fig: go.Figure = GDPSummaryTable.build_summ_bar_chart(years, employment_values, units, title, dtype=dtype)
        return fig

    @staticmethod
    def display_gdp_per_worker_barchart(df: pd.DataFrame,
                                        st=default_state,
                                        dtype="int",
                                        start=default_start_year,
                                        end=default_end_year) -> go.Figure:

        years = [str(year) for year in range(start, end)]
        title = f'{st} Annual GDP Per Employee ({years[0]} - {years[-1]})'
        total_employment: pd.Series = df.iloc[14,].copy(deep=True)
        te_data = total_employment[years].copy(deep=True)
        te_data = pd.to_numeric(te_data, errors='coerce').round().astype(int)
        # print(f"te_data: {te_data}")
        real_gdp: pd.Series = df.iloc[0,].copy(deep=True)
        rgdp_data = real_gdp[years].copy(deep=True)
        rgdp_data = pd.to_numeric(rgdp_data, errors='coerce').round().astype(float)
        if "millions" in real_gdp['Unit'].lower():
            rgdp_data *= 1000000  # convert from millions to dollars
        gdp_per_worker: pd.Series = rgdp_data / te_data
        # print(f"gdp_per_capita: {gdp_per_capita}")
        gdp_pc = pd.to_numeric(gdp_per_worker, errors='coerce').round().astype(int)
        units = "GDP per Capita in Dollars"
        gdp_per_worker_values = list(gdp_pc.copy())
        print(f"gdp_per_capita_values: {gdp_per_worker_values}")
        fig: go.Figure = GDPSummaryTable.build_summ_bar_chart(years, gdp_per_worker_values, units, title, dtype=dtype)
        return fig

#     get Population by state for 2008-2024


    def display_gdp_per_capita_barchart(self,
                                        df: pd.DataFrame,
                                        st=default_state,
                                        dtype="int",
                                        start=default_start_year,
                                        end=default_end_year,
                                        pop=Population()) -> go.Figure:

        years = [str(year) for year in range(start, end)]
        title = f'{st} Annual Real GDP Per Capita ({years[0]} - {years[-1]})'
        total_employment: pd.Series = df.iloc[14,].copy(deep=True)
        tpop_data:List[StPop] = pop.active_states.find_state_years(st, list(range(start, end)))
        tpop_data.sort(key=lambda x: x.year)
        tpop_vals = [spop.population for spop in tpop_data]
        tpop_vals = pd.to_numeric(tpop_vals, errors='coerce').astype(int)
        # print(f"te_data: {te_data}")
        real_gdp: pd.Series = df.iloc[0,].copy(deep=True)
        rgdp_data = real_gdp[years].copy(deep=True)
        rgdp_data = pd.to_numeric(rgdp_data, errors='coerce').round().astype(float)
        if "millions" in real_gdp['Unit'].lower():
            rgdp_data *= 1000000  # convert from millions to dollars
        gdp_per_capita: pd.Series = rgdp_data / tpop_vals
        print(f"gdp_per_capita: {gdp_per_capita}")
        gdp_pcap = pd.to_numeric(gdp_per_capita, errors='coerce').round().astype(int)
        units = "Real GDP per Capita / 2017 Dollars"
        gdp_per_capita_values = list(gdp_pcap.copy())
        print(f"gdp_per_capita_values: {gdp_per_capita_values}")
        fig: go.Figure = GDPSummaryTable.build_summ_bar_chart(years, gdp_per_capita_values, units, title, dtype=dtype)
        return fig


class AllSummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "All States Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SUMMARY__ALL_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data = self.sclean(self.raw_df, is_all=True)
        self.df = data['df']
        self.meta_df = data['meta_df']



class NDSummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "North Dakota Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SASUMMARY_ND_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data: dict = self.sclean(self.raw_df, is_all=False)
        self.df = data['df']
        self.meta_df = data['meta_df']



class MESummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "Maine Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SASUMMARY_ME_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data: dict = self.sclean(self.raw_df, is_all=False)
        self.df = data['df']
        self.meta_df = data['meta_df']


class TXSummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "Texas Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SASUMMARY_TX_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data: dict = self.sclean(self.raw_df, is_all=False)
        self.df = data['df']
        self.meta_df = data['meta_df']




class MNSummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "Minnesota Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SASUMMARY_MN_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data: dict = self.sclean(self.raw_df, is_all=False)
        self.df = data['df']
        self.meta_df = data['meta_df']


class WVSummaryTable(GDPSummaryTable):
    def __init__(self):
        super().__init__()
        self.description = "West Virginia Summary GDP Table 1998 - 2024"
        self.fn = f"{self.summary_dir}/SASUMMARY_WV_1998_2024.csv"
        self.raw_df: pd.DataFrame = pd.read_csv(self.fn)
        data: dict = self.sclean(self.raw_df, is_all=False)
        self.df = data['df']
        self.meta_df = data['meta_df']
