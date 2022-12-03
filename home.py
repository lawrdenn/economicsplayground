import streamlit as st
import pandas as pd
from functions import backend
import random
import time

st_style = """
            <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}

                [data-testid="stSidebarNav"] {
                    background-image: url(https://i.imgur.com/wh23Aza.png);
                    background-repeat: no-repeat;
                    padding-top: 120px;
                    background-position: 20px 20px;
                }
                [data-testid="stSidebarNav"]::before {
                    margin-left: 20px;
                    margin-top: 20px;
                    font-size: 30px;
                    position: relative;
                    top: 100px;
                }
                @import url('https://fonts.googleapis.com/css2?family=Tonnelier:wght@100&display=swap');

                html, body, div [class*="css"]  {
                font-family: 'Tonnelier', sans-serif;
                }
            
            </style>
            """

st.markdown(st_style, unsafe_allow_html=True)

def create_session_state_keys(key_dict):
    for key in key_dict.keys():
        if key not in st.session_state:
            st.session_state[key] = key_dict[key]

create_session_state_keys({'unique_keys': [0], 'master_data_obj': backend.IMF_data()})

IMF_code_obj = backend.IMF_codes()

DEFAULT_SELECT = 'Select Option'
PLOTTING_OPTIONS = ['Line Graph']

macro_data_freq = IMF_code_obj.get_frequencies_text_items()
macro_data_options = IMF_code_obj.get_indicator_text_items()
macro_data_options = [DEFAULT_SELECT] + [o for o in macro_data_options if ',' not in o]
countries = [DEFAULT_SELECT] + IMF_code_obj.get_ref_area_text_items()

def make_grid(cols, rows):
    grid = [0] * cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid

def create_data_item(n, macro_data_options, countries, key):
    grid_name = f'💾 Data {n}'

    with input_grid_layout[n][0].expander(grid_name):
        countries_selected = st.selectbox('Select Country:', countries, key=f'countries_selected_{key}')
        macro_data_selected = st.selectbox('Select Data:', macro_data_options, key=f'macro_data_selected_{key}')
        # add_forecast = st.multiselect('Add Forecast', ['Linear Regression', 'ARIMA', 'SARIMA', 'Monte Carlo'], key=f'forecast_{key}')

        if n != 1:
            delete_button = st.button('Delete Data', key=f'delete_button_{key}')

            if delete_button:
                with st.spinner('Removing data'):
                    time.sleep(0.15)
                    del st.session_state['unique_keys'][n - 1]
                    try:
                        st.session_state['master_data_obj'].drop_data(n - 1)
                        del st.session_state[f'{n}_macro_data_selected']
                        del st.session_state[f'{n}_countries_selected']
                    except Exception:
                        pass # inputs are empty

                    st.experimental_rerun()
        else:
            delete_button = False

        data_exists = True
        if all([countries_selected != DEFAULT_SELECT, macro_data_selected != DEFAULT_SELECT]):
            indicator = IMF_code_obj.text_to_code(macro_data_selected, 'INDICATOR')
            ref_area = IMF_code_obj.text_to_code(countries_selected, 'REF_AREA')
            freq = IMF_code_obj.text_to_code(macro_freq_selected, 'FREQ')

            if not IMF_code_obj.check_code_valid(f'{freq}-{ref_area}-{indicator}'):
                st.error(f' {macro_freq_selected} {macro_data_selected} for {countries_selected} does not exist', icon="❌")
                data_exists = False

            if f'{key}_has_data' not in st.session_state:
                st.session_state[f'{key}_has_data'] = None

    with input_grid_layout[n][0]:
        with st.spinner(f'Getting {macro_freq_selected} {macro_data_selected} for {countries_selected}'):
            if all([countries_selected != DEFAULT_SELECT, macro_data_selected != DEFAULT_SELECT]) and data_exists:
                data_to_add = f'IMF/CPI/{freq}.{ref_area}.{indicator}'

                if not st.session_state[f'{key}_has_data']:
                    st.session_state['master_data_obj'].add_new_data(data_to_add, f'{countries_selected} {macro_data_selected} ({macro_freq_selected})')
                    st.session_state[f'{key}_has_data'] = f'IMF/CPI/{freq}.{ref_area}.{indicator}'

                elif st.session_state[f'{key}_has_data'] != data_to_add:
                    col_to_drop = st.session_state['master_data_obj'].master_data.set_index('Date').columns[n - 1]
                    col_idx_to_drop = st.session_state['master_data_obj'].master_data.set_index('Date').columns.to_list().index(col_to_drop)

                    st.session_state['master_data_obj'].drop_data(col_idx_to_drop)

                    st.session_state['master_data_obj'].add_new_data(data_to_add, f'{countries_selected} {macro_data_selected} ({macro_freq_selected})')
                    st.session_state[f'{key}_has_data'] = f'IMF/CPI/{freq}.{ref_area}.{indicator}'
                else:
                    pass

    return macro_data_selected, countries_selected, delete_button

def reset_plot_selection():
    st.session_state['plot_selection'] = []

input_tab, plot_tab, data_tab = st.tabs(['🔍 Select Data', '📈 View Graph', '📁 View & Download Data'])

with input_tab:
    global input_grid_layout
    input_grid_layout = make_grid(10, [1]) # n cols, col width (with length of n of rows)
    add_button = input_grid_layout[len(st.session_state['unique_keys']) + 3][0].button('Add Data')

    if add_button:
        key = random.randint(0, 9999)

        while key in st.session_state['unique_keys']:
            key = random.randint(0, 9999)

        st.session_state['unique_keys'].append(key)

    macro_freq_selected = input_grid_layout[0][0].selectbox('Select Frequency:', macro_data_freq)

    delete_buttons = []
    for key in st.session_state['unique_keys']:
        n = st.session_state['unique_keys'].index(key) + 1
        macro_data_selected, countries_selected, delete_button = create_data_item(n, macro_data_options, countries, key)

        if all([countries_selected != DEFAULT_SELECT, macro_data_selected != DEFAULT_SELECT]):
            st.session_state[f'{n}_macro_data_selected'] = macro_data_selected
            st.session_state[f'{n}_countries_selected'] = countries_selected

        delete_buttons.append(delete_button)

with plot_tab:
    if not st.session_state['master_data_obj'].master_data.empty:
        plot_obj = backend.plotting(st.session_state['master_data_obj'].master_data)

        selected = st.multiselect('Select Plots', ['Data Summary', 'Line Plot', 'Area Plot'], on_change=reset_plot_selection)

        # Ensures plots stay for existing data after a data item is deleted
        if not selected and 'plot_selection' in st.session_state:
            selected = st.session_state['plot_selection']
        
        for choice in selected:
            if choice == 'Line Plot':
                st.markdown('**Line Plot**')
                st.plotly_chart(plot_obj.line_plot(), use_container_width=False, theme='streamlit', config=dict(displayModeBar=False))
            
            if choice == 'Area Plot':
                st.markdown('**Area Plot**')
                st.plotly_chart(plot_obj.area_plot(), use_container_width=False, theme='streamlit', config=dict(displayModeBar=False))

            if choice == 'Data Summary':
                st.markdown('**Data Summary**')
                st.table(st.session_state['master_data_obj'].master_data.describe())

        st.session_state['plot_selection'] = selected
    else:
        st.write('No data to plot')

with data_tab:
    @st.experimental_memo
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    if not st.session_state['master_data_obj'].master_data.empty:
        csv = convert_df(st.session_state['master_data_obj'].master_data)

        st.dataframe(st.session_state['master_data_obj'].master_data.sort_values('Date', ascending=False).set_index('Date'))
        st.download_button('Download Data', csv, 'economics-playground-export.csv') # add google analytics to this
    else:
        st.write('No data to view')
    


