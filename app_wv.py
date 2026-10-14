import streamlit as st
from emp_bundles import SAEmpGdpMgr as Mgr
import plotly_displays

state="West Virginia"
tab1, tab2, tab3, tab4 = st.tabs(["GDP", "Surplus", "Taxes-Subsidies", "Comp/Emp"])
md_nd_files: dict[str, str] = {'intro_nd':'markdown/gdp_intro_a_nd.md',
                            'rgdp_nd':'markdown/r_gdp_nd.md'}
md_wv_files: dict[str, str] = {'intro_wv':'markdown/gdp_intro_a_wv.md',
                            'rgdp_wv':'markdown/r_gdp_wv.md',
                               'totals_wv':'markdown/totals_wv.md',
                               'rgdp_percap':'images/wv_percap_gdp.png'}

with tab1:
    st.write(f"{state} tab1")
    st.header(f"2024 {state} Gross Domestic Product, by Industry Category")
    gdp_mgr = Mgr(sa_name='WV', doc='GDP')
    gdp_displays = plotly_displays.GdpDisplays(gdp_mgr)
    gdp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(gdp_fig)

    # textContent = "This is some text."
    md_intro_fn = md_wv_files['intro_wv']
    with open(md_intro_fn, 'r') as f:
        intro_text = f.read()
    st.markdown(intro_text)

    #  Real GDP


    r_gdp_mgr = Mgr(sa_name='WV', doc='REAL_GDP')
    st.header(f"2024 {r_gdp_mgr.state_name} Real GDP by Industry Category")
    r_gdp_displays = plotly_displays.GdpDisplays(r_gdp_mgr)
    r_gdp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(r_gdp_fig,key='r_gdp_fig')

    md_rgdp_fn = md_wv_files['rgdp_wv']
    with open(md_rgdp_fn, 'r') as ff:
        rgdp_text = ff.read()
    st.markdown(rgdp_text)

    # REAL GDP totals: 2017-2024

    data_all = r_gdp_mgr.data_all_class
    gdp_totals = gdp_displays.sagdp_totals_yrs()
    st.plotly_chart(gdp_totals, key='gdp_totals')
    with open('markdown/gdp_totals_nd.md', 'r') as f:
        gdp_totals_nd_text = f.read()
    st.markdown(gdp_totals_nd_text)

    # real per capita gdp

    st.write(f"### GDP PER CAPITA for {r_gdp_mgr.state_name}:")
    st.image("./images/wv_percap_gdp.png")


    # median family income


    st.write(f"### Median family income for {r_gdp_mgr.state_name} 2000-2024")
    fig_med = r_gdp_displays.median_comp_2000_2024()
    st.plotly_chart(fig_med, key='fig_med')


with tab2:
    st.write("surpluses")
    st.header(f"{state} Surpluses by Industry Category")
    surp_mgr = Mgr(sa_name='WV', doc='SURPLUS')
    sur_gdp_displays = plotly_displays.GdpDisplays(surp_mgr)
    surp_fig = sur_gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(surp_fig)
    with open('markdown/surplus_wv.md', 'r') as f:
        surplus_nd_text = f.read()
    st.markdown(surplus_nd_text)

    # st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
with tab3:
    st.write("North Dakota tab3")
    st.header(f"{state} Taxes by Industry Category")
    tax_mgr = Mgr(sa_name='WV', doc='TAX')
    tax_gdp_displays = plotly_displays.GdpDisplays(tax_mgr)
    tax_fig = tax_gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(tax_fig, key='tax_fig')

    st.header(f"{state} Subsidies by Industry Category")
    sub_mgr = Mgr(sa_name='WV', doc='SUBS')
    sub_gdp_displays = plotly_displays.GdpDisplays(sub_mgr)
    sub_fig = sub_gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(sub_fig, key='sub_fig')

    st.header(f"{state} Taxes Minus Subsidies by Industry Category")
    tax_sub_mgr = Mgr(sa_name='WV', doc='TAX-SUBS')
    tax_sub_gdp_displays = plotly_displays.GdpDisplays(tax_sub_mgr)
    tax_sub_fig = tax_sub_gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(tax_sub_fig, key='tax_sub_fig')

with tab4:
    st.write("North Dakota tab4")
    st.header(f"{state} Employee Compensation by Industry Category")
    comp_mgr = Mgr(sa_name='ND', doc='COMP')
    comp_gdp_displays = plotly_displays.GdpDisplays(comp_mgr)
    comp_fig = comp_gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(comp_fig)

    st.header(f"{state} Employment by Industry Category")
    emp_mgr = Mgr(sa_name='WV', doc='EMP')
    emp_displays = plotly_displays.EmpDisplays(emp_mgr)
    emp_fig = emp_displays.emp_by_industry_r2()
    st.plotly_chart(emp_fig, key='emp_fig')