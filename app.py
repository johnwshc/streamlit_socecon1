import streamlit as st
from emp_bundles import SAEmpGdpMgr as Mgr
import plotly_displays

tab1, tab2, tab3, tab4 = st.tabs(["GDP", "Surplus", "Taxes-Subsidies", "Comp/Emp"])
md_files: dict[str, str] = {'intro_nd':'markdown/gdp_intro_a_nd.md',
                            'rgdp_nd':'markdown/r_gdp_nd.md'}

with tab1:
    st.write("North Dakota tab1")
    st.header("2024 North Dakota Gross Domestic Product, by Industry Category")
    gdp_mgr = Mgr(sa_name='ND', doc='GDP')
    gdp_displays = plotly_displays.GdpDisplays(gdp_mgr)
    gdp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(gdp_fig)

    # textContent = "This is some text."
    md_intro_fn = md_files['intro_nd']
    with open(md_intro_fn, 'r') as f:
        intro_text = f.read()
    st.markdown(intro_text)


    st.header("2024 Real GDP by Industry Category")
    r_gdp_mgr = Mgr(sa_name='ND', doc='REAL_GDP')
    gdp_displays = plotly_displays.GdpDisplays(r_gdp_mgr)
    r_gdp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(r_gdp_fig)

    md_rgdp_fn = md_files['rgdp_nd']
    with open(md_rgdp_fn, 'r') as ff:
        rgdp_nd_text = ff.read()
    st.markdown(rgdp_nd_text)

    # GDP totals: 2017-2024
    data_all = r_gdp_mgr.data_all_class
    gdp_totals = gdp_displays.sagdp_totals_yrs()
    st.plotly_chart(gdp_totals)
    with open('markdown/gdp_totals_nd.md', 'r') as f:
        gdp_totals_nd_text = f.read()
    st.markdown(gdp_totals_nd_text)


with tab2:
    st.write("North Dakota tab2")
    st.header("North Dakota Surpluses by Industry Category")
    surp_mgr = Mgr(sa_name='ND', doc='SURPLUS')
    gdp_displays = plotly_displays.GdpDisplays(surp_mgr)
    surp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(surp_fig)
    

    # st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
with tab3:
    st.write("North Dakota tab3")
    st.header("North Dakota Taxes by Industry Category")
    # st.image("https://static.streamlit.io/examples/owl.jpg", width=200)
    tax_mgr = Mgr(sa_name='ND', doc='TAX')
    gdp_displays = plotly_displays.GdpDisplays(tax_mgr)
    tax_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(tax_fig)

    st.header("North Dakota Subsidies by Industry Category")
    sub_mgr = Mgr(sa_name='ND', doc='SUBS')
    gdp_displays = plotly_displays.GdpDisplays(sub_mgr)
    sub_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(sub_fig)

    st.header("North Dakota Taxes Minus Subsidies by Industry Category")
    tax_sub_mgr = Mgr(sa_name='ND', doc='TAX-SUBS')
    gdp_displays = plotly_displays.GdpDisplays(tax_sub_mgr)
    tax_sub_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(tax_sub_fig)

with tab4:
    st.write("North Dakota tab4")
    st.header("North Dakota Employee Compensation by Industry Category")
    comp_mgr = Mgr(sa_name='ND', doc='COMP')
    gdp_displays = plotly_displays.GdpDisplays(comp_mgr)
    comp_fig = gdp_displays.sa_gdp_by_industry_r2()
    st.plotly_chart(comp_fig)

    st.header("North Dakota Employment by Industry Category")
    emp_mgr = Mgr(sa_name='ND', doc='EMP')
    emp_displays = plotly_displays.EmpDisplays(emp_mgr)
    emp_fig = emp_displays.emp_by_industry_r2()
    st.plotly_chart(emp_fig)