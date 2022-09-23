from random import sample
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
import markdown


class BasicAnalyze:
  """
  This application requires Python 3.10 or later.
  """

  def __init__(self) -> None:
    now = datetime.datetime.now()
    self.create_folder_path = os.path.join(pathlib.Path(__file__).parent, "record",now.strftime("analyzed_%Y%m%d-%H%M%S"))
    os.makedirs(self.create_folder_path, mode=0o777, exist_ok=True)
    self.write_record("# This is analyzed record of CSV files.")
  
  def write_record(self, content):
    with open(os.path.join(self.create_folder_path,'result.md'), 'a') as f:
      f.write(content)
      f.write("\n\n")
      f.close()

  def encoding_mark_down_to_html(self):
    with open(os.path.join(self.create_folder_path,'result.md'), "r") as f:
      sample = f.read()
      f.close()

    md = markdown.Markdown(extensions=['tables'])

    with open(os.path.join(self.create_folder_path,'result.html'), 'a') as f_html:
      f_html.write(md.convert(sample))
      f_html.close()

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
        text = (
          f"""
## csv file analyzed record

csv file: {csv_path} 

### overview
          """)
        self.write_record(text)
        self.write_record(self.df_record.to_markdown())
        self.encoding_mark_down_to_html()
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
    df.loc["Max"] = series.max().round(3)
    df.loc["Min"] = series.min().round(3)
    df.loc["Mean"] = series.mean().round(3)  
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
    df.loc["Max"] = series.max().round(3)
    df.loc["Min"] = series.min().round(3)
    df.loc["Mean"] = series.mean().round(3) 
    if series.max() <=1 and series.min() >=0:
      if len(series.unique())<=2:
        df.loc["Data_Type"] = "Ratio Data"
    else:
      df.loc["Data_Type"] = "Float Data"
      df.round({"Mean":3})
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
        if len(series.unique()) < 3:
          df.loc["Data_Type"] = "Binary String Data"
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
    df.loc["Max"] = series.max().round(3)
    df.loc["Min"] = series.min().round(3)
    df.loc["Mean"] = series.mean().round(3) 
    df.loc["Data_Type"] = "Datetime Data"
    self.df_record = pd.concat([self.df_record,df], axis = 1)
  ##E def
  def __del__(self):
    pass

class GraphMaker:
  def __init__(self, location) -> None:
    self.save_file_location = location

  

  def __del__(self):
    pass

if __name__ =="__main__":
  BA = BasicAnalyze()
  BA.settings(csv_files = [r".\test.csv"])

