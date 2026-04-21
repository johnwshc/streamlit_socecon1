# %%
# def show_nd_gdp2_table(dff_classes: pd.DataFrame, title: str, col_labels: Tuple | None = None) -> None:
#     import plotly.graph_objects as go
#
#     # If no custom labels provided, use the dataframe column names
#     header_vals = col_labels if col_labels is not None else list(dff_classes.columns)
#
#     # Build cell values in the same column order as the dataframe so header labels line up
#     cells_vals = [dff_classes[col] for col in dff_classes.columns]
#
#     fig2 = go.Figure(data=[go.Table(
#         header=dict(values=header_vals,
#                     fill_color='blue',
#                     align='left'),
#         cells=dict(values=cells_vals,
#                    fill_color='gray',
#                    align='left'))
#     ])
#
#     # Set title and layout options here
#     fig2.update_layout(title_text=title, title_x=0.5, margin=dict(t=40, l=10, r=10))
#     fig2.show()
# ctitle = "2024 North Dakota GDP by Industry Class, and Category"
# clabels = ('Industry Description', '2024 GDP in Millions', 'Marx-like Category')
# show_nd_gdp2_table(sorted_df_gdp, title=ctitle, col_labels=clabels)

# %% sql


# def show_descs_table(dff_classes: pd.DataFrame, title: str = 'Classification Descriptions',
                     #                      col_labels: list | None = None) -> None:
                     #     import plotly.graph_objects as go
                     #
                     #     # If no custom labels provided, use the dataframe column names
                     #     header_vals = col_labels if col_labels is not None else list(dff_classes.columns)
                     #
                     #     # Build cell values in the same column order as the dataframe so header labels line up
                     #     cells_vals = [dff_classes[col] for col in dff_classes.columns]
                     #
                     #     fig2 = go.Figure(data=[go.Table(
                     #         header=dict(values=header_vals,
                     #                     fill_color='blue',
                     #                     align='left'),
                     #         cells=dict(values=cells_vals,
                     #                    fill_color='gray',
                     #                    align='left'))
                     #     ])
                     #
                     #     # Set title and layout options here
                     #     fig2.update_layout(title_text=title, title_x=0.5, margin=dict(t=40, l=10, r=10))
                     #     fig2.show()
                     #
                     # f = sa_gdp_mgr.df.copy(deep=True)
                     # fn = f"{Config.DATA_DIR}/gdp_short_classes.txt"

