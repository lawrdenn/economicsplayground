import streamlit as st
import json
import random
from dbnomics import fetch_series
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

class IMF_codes:
    def __init__(self):
        self.IMF_code_dict, self.IMF_code_combos = self.__get_code_dict()

    def __get_code_dict(self):
        with open('functions/IMF_CODES/IMF_codes.json', 'r') as f:
            codes = json.load(f)

        with open('functions/IMF_CODES/valid_code_combos.json', 'r') as f:
            valid_code_combos = json.load(f)

        return codes, valid_code_combos
    
    def get_frequencies_text_items(self):
        IMF_freq_code_dict = self.IMF_code_dict['FREQ']
        frequencies_text = [IMF_freq_code_dict[k] for k in IMF_freq_code_dict.keys()]

        return frequencies_text

    def get_ref_area_text_items(self):
        IMF_ref_area_code_dict = self.IMF_code_dict['REF_AREA']
        ref_area_text = [IMF_ref_area_code_dict[k] for k in IMF_ref_area_code_dict.keys()]

        return ref_area_text

    def get_indicator_text_items(self):
        IMF_indicator_code_dict = self.IMF_code_dict['INDICATOR']
        indicator_text = [IMF_indicator_code_dict[k] for k in IMF_indicator_code_dict.keys()]

        return indicator_text

    def code_to_text(self, code, code_type):
        return self.IMF_code_dict[code_type][code]
    
    def text_to_code(self, text, code_type):
        return [k for k in self.IMF_code_dict[code_type].keys() if self.IMF_code_dict[code_type][k] == text.strip()][0]

    def get_valid_codes(self, freq=None, ref_area=None, indicator=None):
        valid_combos = [k for k in self.IMF_code_combos if self.IMF_code_combos[k]]

        valid_freq = [freq]
        valid_ref_areas = [ref_area]
        valid_indicators = [indicator]
        
        if freq and ref_area:
            valid_indicators = [code.split('-')[2] for code in valid_combos if code.split('-')[0] == freq and code.split('-')[1] == ref_area]
            
        elif freq and indicator:
            valid_ref_areas = [code.split('-')[2] for code in valid_combos if code.split('-')[0] == freq and code.split('-')[2] == indicator]
            
        elif ref_area and indicator:
            valid_freq = [code.split('-')[2] for code in valid_combos if code.split('-')[1] == ref_area and code.split('-')[2] == indicator]

        elif freq:
            valid_ref_areas = [code.split('-')[1] for code in valid_combos if code.split('-')[0] == freq]
            valid_indicators = [code.split('-')[2] for code in valid_combos if code.split('-')[0] == freq]
            
        elif ref_area:
            valid_freq = [code.split('-')[0] for code in valid_combos if code.split('-')[1] == ref_area]
            valid_indicators = [code.split('-')[2] for code in valid_combos if code.split('-')[1] == ref_area]
            
        elif indicator:
            valid_freq = [code.split('-')[0] for code in valid_combos if code.split('-')[2] == indicator]
            valid_ref_areas = [code.split('-')[1] for code in valid_combos if code.split('-')[2] == indicator]

        else:
            assert False
            
        return valid_freq, valid_ref_areas, valid_indicators

    def check_code_valid(self, code_combo):
        return self.IMF_code_combos[code_combo]
    

    @st.cache
    def get_random_selections(self, lst, min_n=2, max_n=3):
        choices = [lst[random.randint(0, len(lst) - 1)] for item_n in range(random.randint(min_n, max_n))]

        return choices

    @st.cache
    def get_random_selection(self, lst):
        choice = random.randint(0, len(lst) - 1)

        return choice, lst[choice]
        

class IMF_data:
    def __init__(self):
        self.master_data = pd.DataFrame()

    def __get_data(self, url, y_axis_name):
        data = fetch_series(url)
        data = data[['period', 'value']].dropna()

        data = data.sort_values('period')
        
        data.rename({'period': 'Date'}, axis=1, inplace=True)
        data.rename({'value': y_axis_name}, axis=1, inplace=True)
        
        return data
    
    def add_new_data(self, url, y_axis_name):
        data = self.__get_data(url, y_axis_name)
        
        if self.master_data.empty:
            self.master_data = data
        else:
            self.master_data = pd.merge(self.master_data, data, on='Date', how='outer')
            
    def drop_data(self, n):
        col_to_drop = self.master_data.set_index('Date').columns[n]
        self.master_data.drop(col_to_drop, axis=1, inplace=True)


class plotting:
    def __init__(self, data):
        self.data = data
        self.melted_data = self.__melt_data()
        
    def __melt_data(self):
        return self.data.sort_values('Date').melt(id_vars=['Date'], var_name='Item')
    
    def line_plot(self):
        fig = px.line(self.melted_data, x='Date', y='value', color='Item')

        fig.update_layout(
            xaxis_title = 'Date',
            yaxis_title = 'Value',
            legend=dict(
            yanchor='bottom',
            y=-.45,
            xanchor='left',
            x=0,
            title={'text': None},
            bgcolor='rgba(0, 0, 0, 0)'
          )
        )
        
        return fig
    
    def area_plot(self):
        fig = px.area(self.melted_data, x='Date', y='value', color='Item')

        fig.update_layout(
            xaxis_title = 'Date',
            yaxis_title = 'Value',
            legend=dict(
            yanchor='bottom',
            y=-.45,
            xanchor='left',
            x=0,
            title={'text': None},
            bgcolor='rgba(0, 0, 0, 0)'
          )
        )
        
        return fig






