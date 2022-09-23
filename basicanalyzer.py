import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pathlib
import os
import json
from enum import Enum
import glob
import datetime


class BasicAnalyze:
  """
  This application requires Python 3.10 or later.
  """

  def __init__(self) -> None:
    now = datetime.datetime.now()
    create_folder_path = os.path.join(pathlib.Path(__file__).parent, "record",now.strftime("analyzed_%Y%m%d-%H%M%S"))
    os.makedirs(create_folder_path, mode=0o777, exist_ok=True)


  def settings(self,overwrite = False, csv_files = [], dataframe = None, *args, **kwargs):
    """
    overwrite: when true, change settings
    csv_files: csv file path(s) list
    dataframe: Pandas dataframe
    """
    settings_path = pathlib.Path(__file__).parent

    # read settings
    with open(os.path.join(settings_path,"settings.json"), 'r') as json_file:
      settings_data = json.load(json_file)

    # csv files
    if csv_files:
      for csv_path in csv_files:
        self.df_record = pd.DataFrame(index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
        df = pd.read_csv(csv_path, encoding = settings_data["csv"]["encoding"])
        self.analyze_data_structure(df)
        print(self.df_record)
  ##E def

  def analyze_data_structure(self, dataframe):
    df = dataframe
    print ("start analyze_data")
    for column_name in df.columns:
      str_dtype = df[column_name].dtype

      if "int" in str(str_dtype):
        self.int_analyzer(column_name, df[column_name])
        ## 構造解析へ

      elif "float" in str(str_dtype):
        self.float_analyzer(column_name, df[column_name])
        ## 構造解析へ

      elif "bool" in str(str_dtype):
        self.bool_analyzer(column_name, df[column_name])

      elif "object" in str(str_dtype):
        self.object_analyzer(column_name, df[column_name])

      elif "datetime" in str(str_dtype):
        self.datetime_analyzer(column_name, df[column_name])
      ##E if
    ##E for
  ##E def

  def int_analyzer(self,column_name, series):
    df = pd.DataFrame(columns = [column_name] ,index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
    df.loc["Type"] = series.dtype
    df.loc["Exist_Nan"] = series.isna().sum()
    df.loc["Num_Data"] = series.count()
    df.loc["Max"] = series.max()
    df.loc["Min"] = series.min()
    df.loc["Mean"] = series.mean()    
    if series.max() <=1 and series.min() >=0:
      if len(series.unique())<=2:
        df.loc["Data_Type"] = "Binary Data"
    else:
      df.loc["Data_Type"] = "Numeric Data"
    self.df_record = pd.concat([self.df_record,df], axis = 1)

  ##E def
  def float_analyzer(self, column_name, series):
    df = pd.DataFrame(columns = [column_name] ,index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
    df.loc["Type"] = series.dtype
    df.loc["Exist_Nan"] = series.isna().sum()
    df.loc["Num_Data"] = series.count()
    df.loc["Max"] = series.max()
    df.loc["Min"] = series.min()
    df.loc["Mean"] = series.mean()    
    if series.max() <=1 and series.min() >=0:
      if len(series.unique())<=2:
        df.loc["Data_Type"] = "Ratio Data"
    else:
      df.loc["Data_Type"] = "Float Data"
    self.df_record = pd.concat([self.df_record,df], axis = 1)

  ##E def
  def bool_analyzer(self, column_name, series):
    df = pd.DataFrame(columns = [column_name] ,index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
    df.loc["Type"] = series.dtype
    df.loc["Exist_Nan"] = series.isna().sum()
    df.loc["Num_Data"] = series.count()
    df.loc["Max"] = "Not Defined"
    df.loc["Min"] = "Not Defined"
    df.loc["Mean"] = "Not Defined"    
    df.loc["Data_Type"] = "Bool Data"
    self.df_record = pd.co
  
  ##E def
  def object_analyzer(self, column_name, series):
    df = pd.DataFrame(columns = [column_name] ,index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
    df.loc["Type"] = series.dtype
    df.loc["Exist_Nan"] = series.isna().sum()
    df.loc["Num_Data"] = series.count()
    df.loc["Max"] = "Not Defined"
    df.loc["Min"] = "Not Defined"
    df.loc["Mean"] = "Not Defined"  
    flag_num = False
    flag_datetime = False
    for content in series:
      if isinstance(content,int):
        flag_num = True
      elif isinstance(content, float):
        flag_num = True
      elif isinstance(content, datetime.date):
        flag_datetime = True
      elif isinstance(content, datetime.datetime):
        flag_datetime = True
    else:
      if flag_num or flag_datetime:
        df.loc["Data_Type"] = "Muti-Type Data"
      else:
        df.loc["Data_Type"] = "String Data"
    ##E for
    self.df_record = pd.concat([self.df_record,df], axis = 1)
  ##E def

  def datetime_analyzer(self, column_name, series):
    df = pd.DataFrame(columns = [column_name] ,index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
    df.loc["Type"] = series.dtype
    df.loc["Exist_Nan"] = series.isna().sum()
    df.loc["Num_Data"] = series.count()
    df.loc["Max"] = series.max()
    df.loc["Min"] = series.min()
    df.loc["Mean"] = series.mean()     
    df.loc["Data_Type"] = "Datetime Data"
    self.df_record = pd.concat([self.df_record,df], axis = 1)
  ##E def
  def __del__(self):
    pass

if __name__ =="__main__":
  BA = BasicAnalyze()
  BA.settings(csv_files = [r"C:\Users\0720k\myapplications\basic_analyzer\test.csv"])

