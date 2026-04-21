
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from emp_bundles import SAEmpGdpMgr as Mgr
from parse_lncodes2 import LCMeta, LCIndex, parse_file
from pathlib import Path


class GdpDisplays:

    def __init__(self, sdf: pd.DataFrame):
        self.sdf = sdf.copy(deep=True)
        self.short_index: LCIndex = parse_file(Path('data\\gdp_short_classes.txt'))
        long_index = parse_file(Path('data\\gdp_classes.txt'))
        self.sdf['ShortDesc'] = sdf.LineCode.apply(self.short_index.get_description)
        self.sdf.drop(['clean_description'], axis=1, inplace=True)


    def show_nd_gdp_by_industry_category_3(self) -> px.bar:
        df = self.sdf.copy()
        rdf = df.drop([14, 15, 16], axis=0).reset_index(drop=True)
        sorted_df = rdf.sort_values(by='2024', ascending=False)

        fig = px.bar(sorted_df,
                     x='ShortDesc',
                     y='2024',
                     color='category',
                     category_orders={'ShortDesc': list(sorted_df['ShortDesc'])},
                     labels={'2024': '2024 N. Dakota GDP in millions', 'ShortDesc': 'Public and Private Industries',
                             'category': 'Marx-like Category'},
                     title='North Dakota GDP by Industry Category'
                     )
        return fig


    def show_nd_gdp_by_industry_category(self) -> px.bar:
        df = self.sdf.copy()

        sorted_df = self.sdf.sort_values(by='2024', ascending=False)


        fig = px.bar(
            sorted_df,
            x='ShortDesc',
            y='2024',
            color='category',
            category_orders={'ShortDesc': list(sorted_df['ShortDesc'])},
            labels={'2024': '2024 N. Dakota GDP in millions', 'ShortDesc': 'Public and Private Industries', 'category': 'Marx-like Category'},
            title='North Dakota GDP by Industry Category'
        )
        # fig.show()

        return fig

    def show_nd_gdp_by_industry_category_2(self) -> px.bar:
        sorted_df = self.sdf.sort_values(by='2024', ascending=False)

        fig = px.bar(
            sorted_df,
            x='ShortDesc',
            y='2024',
            color='category',
            category_orders={
                'category': ['service', 'production', 'public', 'agricultural'],
                'ShortDesc': list(sorted_df['ShortDesc'])
            },
            labels={
                '2024': '2024 N. Dakota GDP in millions',
                'ShortDesc': 'Public and Private Industries',
                'category': 'Category'
            },
            title='North Dakota GDP by Industry Category'
        )
        return fig


    def show_nd_gdp_by_industry_category_c(self) -> px.bar:
        category_order = {
            "production": 0,
            "service": 1,
            "public": 2,
            "agricultural": 3
        }

