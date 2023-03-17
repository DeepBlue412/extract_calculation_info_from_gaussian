
# coding: utf-8
#!/usr/bin/python
# Author : DeepBlue

import pandas as pd

data = pd.read_csv("calculation_result.csv")

data =data.sort_values(by = ['molecule_type','energy_type','density_functional','bassis_set','method','TDA','TD_option','PCM','PCM_option','initial_structure'])

data.to_csv("calculation_result.csv",sep = ',',index = False)




