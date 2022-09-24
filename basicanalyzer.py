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
import statsmodels.api as sm
import statsmodels.formula.api as smf
from see import see
import scipy.stats as stats
import shutil

class BasicAnalyze:
  """
  This application requires Python 3.10 or later.
  """

  def __init__(self) -> None:
    now = datetime.datetime.now()
    self.create_folder_path = os.path.join(pathlib.Path(__file__).parent, "record",now.strftime("analyzed_%Y%m%d-%H%M%S"))
    os.makedirs(self.create_folder_path, mode=0o777, exist_ok=True)
    shutil.copy2(os.path.join(pathlib.Path(__file__).parent,"src","style.css"), os.path.join(self.create_folder_path,"style.css"))
    self.write_record("# This is analyzed record of CSV files.")
  
  def write_record(self, content):
    with open(os.path.join(self.create_folder_path,'result.md'), 'a', encoding="utf-8") as f:
      f.write(content)
      f.write("\n\n")
      f.close()

  def encoding_mark_down_to_html(self):
    with open(os.path.join(self.create_folder_path,'result.md'), "r") as f:
      sample = f.read()
      f.close()

    md = markdown.Markdown(extensions=['tables',"toc"])

    with open(os.path.join(self.create_folder_path,'result.html'), 'a') as f_html:
      f_html.write(
"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="style.css">
  <title>Document</title>
</head>
<body>
\n\n
"""
      )
      f_html.write(md.convert(sample))
      f_html.write(
"""
\n\n
</body>
</html>
"""
      )
      
      f_html.close()

      return str(os.path.join(self.create_folder_path,'result.html'))

  def analyze(self,overwrite = False, csv_files = [], dataframe = None, *args, **kwargs):
    """
    overwrite: when true, change settings
    csv_files: csv file path(s) list
    dataframe: Pandas dataframe
    """
    settings_path = pathlib.Path(__file__).parent
    record_path = os.path.join(pathlib.Path(__file__).parent, "record","record.csv")
    
    
    # read settings
    with open(os.path.join(settings_path,"settings.json"), 'r') as json_file:
      settings_data = json.load(json_file)

    # csv files
    if csv_files:
      for csv_path in csv_files:
        self.df_record = pd.DataFrame(index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
        df = pd.read_csv(csv_path, encoding = settings_data["csv"]["encoding"])
        list_record =[]
        df_record_csv = pd.read_csv(record_path)
        list_record.append(len(df_record_csv)+1)
        list_record.append(self.create_folder_path)
        self.analyze_data_structure(df)
        print(self.df_record)
        text = (
          f"""
## csv file analyzed record

csv file: {csv_path} 

## overview
          """)
        self.write_record(text)
        self.write_record(self.df_record.to_markdown())

        # Make Graph
        dfT = self.df_record.T
        GM = GraphMaker(self.create_folder_path, dfT, df, csv_path)

        # Make graph 1 each
        list_graph_data = GM.hist_plot()

        for content in list_graph_data:
          link = content = '.'+ content[content.rfind('\\'):]

          text6 = (
f"""
## Histgram and Q-Q plot

Histgram and Q-Q plot

[![]({link})]({link})

"""          
          )
          self.write_record(text6)

        heat_map_path = GM.heat_map()
        heat_map_path = '.'+ heat_map_path[heat_map_path.rfind('\\'):]
        text2 = (
f"""
## Heatmap of correlation

correlation overview

[![]({heat_map_path})]({heat_map_path})

"""          
        )
        self.write_record(text2)
        list_scatter_path = GM.scatter_plot()
        for content in list_scatter_path:
          link = content = '.'+ content[content.rfind('\\'):]

          text3 = (
f"""
## Scatter of correlation

Scatter plot

[![]({link})]({link})

"""          
          )
          self.write_record(text3)
        ##E for

        SR = StatisticRecord(self.create_folder_path, dfT, df, csv_path)
        text_result = SR.ols_record()

        for text_data in text_result:
          text4 = (f"<pre><code>\n\n{text_data}\n\n</code></pre>\n\n")
          self.write_record(text4)

        str_html_result = self.encoding_mark_down_to_html()
        list_record.append(str_html_result)
        list_record.append(csv_path)
        list_record.append("")
        pd.DataFrame([list_record]).to_csv(record_path, mode="a", header=False,index=False)


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
        df.loc["Data_Type"] = "Binary Int Data"
    elif len(series.unique())/len(series) < 0.1:
      df.loc["Data_Type"] = "Categorical Int Data"
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
        elif len(series.unique())/len(series) < 0.1:
          df.loc["Data_Type"] = "Categorical String Data"
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

class StatisticRecord:
  def __init__(self, location, dataframe, df, csv_path) -> None:
    self.save_file_location = location
    self.structure_data = dataframe # dataframe, 
    self.df = df
    self.csv_name = csv_path[csv_path.rfind("\\")+1:csv_path.rfind(".")]

  def ols_record(self):
    _df = self.df
    list_record = []
    _df.dropna(inplace=True)
    for xindex, x_column in enumerate(_df.columns):
      for yindex, y_column in enumerate(_df.columns):
        if xindex < yindex:
          if ("int" or "float") in str(_df[x_column].dtype) and ("int" or "float") in str(_df[y_column].dtype):
            model = sm.OLS(_df[y_column] ,_df[x_column])
            res = model.fit()
            _text = x_column + "_vs_" + y_column + "\n\n" + str(res.summary()) 
            list_record.append(_text)
    return list_record
  def __del__(self):
    pass


class GraphMaker:
  def __init__(self, location, dataframe, df, csv_path) -> None:
    self.save_file_location = location
    self.structure_data = dataframe # dataframe, 
    self.df = df
    self.csv_name = csv_path[csv_path.rfind("\\")+1:csv_path.rfind(".")]


  def heat_map(self) -> str:
    list_index = self.structure_data[self.structure_data.Data_Type.str.contains('Int') | self.structure_data.Data_Type.str.contains('Float') | self.structure_data.Data_Type.str.contains('Date')].index
    fig, ax = plt.subplots(1,1, dpi = 300)
    ax = sns.heatmap(data = self.df[list_index].corr(), annot= True)
    file_path = os.path.join(self.save_file_location, self.csv_name + "-" + "heatmap.png")
    fig.savefig(file_path)
    plt.close()
    return file_path

  def scatter_plot(self)->list:
    list_save_location = []
    list_index = self.structure_data[self.structure_data.Data_Type.str.contains('Int') | self.structure_data.Data_Type.str.contains('Float') | self.structure_data.Data_Type.str.contains('Date')].index
    # num_plots = len(self.df[list_index])
    for xindex, x_column in enumerate(list_index):
      for yindex, y_column in enumerate(list_index):
        if xindex < yindex:
          fig, ax = plt.subplots(1, 1,dpi = 300)
          ax = sns.scatterplot(data = self.df , x = x_column, y=y_column)
          # print (self.df.head(), "x", x_column, "y", y_column )
          ax.set_title(x_column + " vs " + y_column)
          file_path = os.path.join(self.save_file_location, self.csv_name + "-" + x_column + "_vs_" + y_column + "-" + "scatterplot.png")
          fig.savefig(file_path)
          plt.close()
          list_save_location.append(file_path)
      ##E for
    ##E for
    return list_save_location

  def hist_plot(self):
    list_save_location = []

    list_index = self.structure_data[self.structure_data.Data_Type.str.contains('Int') | self.structure_data.Data_Type.str.contains('Float') | self.structure_data.Data_Type.str.contains('Date')].index
    for column in list_index:
      fig, (ax1, ax2) = plt.subplots(1,2, figsize = (20, 10))
      sns.histplot(data = self.df, x = column, kde = True, ax = ax1)
      sm.qqplot(self.df[column].values, ax=ax2)

      file_path = os.path.join(self.save_file_location, self.csv_name + "-" + column + "-" + "Q-Q_plot.png")
      ax1.set_title("Histgram of " + column)
      ax2.set_title("Q-Q plot of " + column)
      fig.savefig(file_path)
      plt.close()
      list_save_location.append(file_path)
    return list_save_location

  def __del__(self):
    pass

if __name__ =="__main__":
  BA = BasicAnalyze()
  BA.analyze(csv_files = [r".\test.csv",r".\test.csv"])

