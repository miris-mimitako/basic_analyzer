import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pathlib
import os
import json
import datetime
import statsmodels.api as sm
from scipy.stats import f_oneway
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
    # HTML initialize
    self.id = 0
    self.write_record("<!DOCTYPE html>")
    self.write_record('<html lang="en">')
    self.write_record('<head>')
    self.write_record('<meta charset="UTF-8">')
    self.write_record('<meta http-equiv="X-UA-Compatible" content="IE=edge">')
    self.write_record('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    self.write_record('<link rel="stylesheet" href="style.css">')
    time_text = now.strftime("%Y%m%d-%H%M%S")
    self.write_record(f'<title>Record {time_text}</title>')
    self.write_record('</head>')
    self.write_record('<body>')
    self.write_record('<main>')
    self.write_record(f'<h1 id = {self.id_count()}>Record</h1>')
    self.list_aside = []
    
    self.list_aside.append("<aside>")
    self.list_aside.append("<ul>")
    self.list_aside.append(f'<li><a class= "list1" href = "#{self.id}">Top</a></li>')

  ##E def 
  def id_count(self):
    self.id +=1
    return self.id

  def write_record(self, content):
    with open(os.path.join(self.create_folder_path,'result.html'), 'a', encoding="utf-8") as f_html:
      f_html.write(content)
      f_html.write("\n")
      f_html.close()

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
        # csv file name
        self.csv_name = csv_path[csv_path.rfind("\\")+1:csv_path.rfind(".")]

        self.df_record = pd.DataFrame(index=["Type", "Num_Data","Exist_Nan", "Data_Type", "Max", "Mean", "Min"])
        
        # dataframe of csv
        self.df = pd.read_csv(csv_path, encoding = settings_data["csv"]["encoding"])

        # record history
        # list_record =[]
        # df_record_csv = pd.read_csv(record_path)
        # list_record.append(len(df_record_csv)+1)
        # list_record.append(self.create_folder_path)

        # csv overview
        self.write_record(f'<h2 id = {self.id_count()}>CSV overview</h2>')
        self.list_aside.append(f'<li><a class= "list2" href = "#{self.id}">CSV overview</a></li>')

        # structure analyze
        self.analyze_data_structure(self.df)
        self.write_record(f'<h3 id = {self.id_count()}>Applicable CSV file</h3>')
        self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Applicable CSV file</a></li>')
        self.write_record(f'<p>csv file: {csv_path}</p>')
        self.write_record(f'<h3 id = {self.id_count()}>Summary of CSV Data {csv_path}</h3>')
        self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Summary of CSV Data {csv_path}</a></li>')
        self.write_record(self.df_record.to_html())
        
        # Make Graph
        dfT = self.df_record.T
        list_num_columns = dfT[dfT.Data_Type.str.contains('Int') | dfT.Data_Type.str.contains('Float') | dfT.Data_Type.str.contains('Date')].index
        list_category_columns = dfT[dfT.Data_Type.str.contains('Cat')| dfT.Data_Type.str.contains('Binary')].index
        
        # Heat map
        heatmap_path = self.heat_map(list_num_columns)
        heatmap_path = "." + heatmap_path[heatmap_path.rfind('\\'):]

        self.write_record(f'<h3 id = {self.id_count()}>Heat Map / Correlations</h3>')
        self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Heat Map / Correlations</a></li>')
        self.write_record(f'<a href="{heatmap_path}"><img alt="" src="{heatmap_path}" /></a>')
        
        # Each column data analysis
        for column_name in list_num_columns:
          self.write_record(f'<h2 id = {self.id_count()}>{column_name}: Each column analyzed record for {column_name}</h2>')
          self.list_aside.append(f'<li><a class= "list2" href = "#{self.id}">{column_name}: Each column analyzed record for {column_name}</a></li>')
          # Histgram
          hist_path = self.hist_plot(column_name)
          hist_path = "." + hist_path[hist_path.rfind('\\'):]
          self.write_record(f'<h3 id = {self.id_count()}>Histgram for {column_name}</h3>')
          self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Histgram for {column_name}</a></li>')
          self.write_record(f'<p>This is histgram and Q-Q plot of {column_name}</p>')
          self.write_record(f'<a href="{hist_path}"><img alt="" src="{hist_path}" /></a>')

          for category_column in list_category_columns:
            if category_column != column_name: # Without duplicate
              catbar_path = self.categorical_hist_plot(column_name, category_column)
              catbar_path = "." + catbar_path[catbar_path.rfind('\\'):]
              self.write_record(f'<h3 id = {self.id_count()}>Category Histgram for {column_name} with {category_column}</h3>')
              self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Category Histgram for {column_name} with {category_column}</a></li>')
              self.write_record(f'<p>This is categorical histgram of  {column_name} with {category_column}</p>')
              self.write_record(f'<a href="{catbar_path}"><img alt="" src="{catbar_path}" /></a>')

              violin_path = self.violin_plot(column_name, category_column)
              violin_path = "." + violin_path[violin_path.rfind('\\'):]
              self.write_record(f'<h3 id = {self.id_count()}>Violin Plot for {column_name} with {category_column}</h3>')
              self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Violin Plot for {column_name} with {category_column}</a></li>')
              self.write_record(f'<p>This is categorical bar plot of  {column_name} with {category_column}</p>')
              self.write_record(f'<a href="{violin_path}"><img alt="" src="{violin_path}" /></a>')

              #One Way Anova...
              f,p = self.one_way_anova(category_column, column_name)
              self.write_record(f'<p>This categories p-value is {p} and f is {f}.</p>')

        ##E for



        # Correlation data analysis

        for x_index, x_column_name in enumerate(list_num_columns):
          for y_index, y_column_name in enumerate(list_num_columns):
            if x_index < y_index :
              self.write_record(f'<h2 id = {self.id_count()}>{x_column_name}-{y_column_name}: Correlation between {x_column_name} and {y_column_name}</h2>')
              self.list_aside.append(f'<li><a class= "list2" href = "#{self.id}">{x_column_name}-{y_column_name}: Correlation between {x_column_name} and {y_column_name}</a></li>')

              # scatter plot
              self.write_record(f'<h3 id = {self.id_count()}>Scatter plot {x_column_name} and {y_column_name}</h3>')
              self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Scatter plot {x_column_name} and {y_column_name}</a></li>')
              scatter_path = self.scatter_plot(x_column_name, y_column_name)
              scatter_path = "." + scatter_path[scatter_path.rfind('\\'):]
              self.write_record(f'<a href="{scatter_path}"><img alt="" src="{scatter_path}" /></a>')

              # ols analyze
              self.write_record(f'<h3 id = {self.id_count()}>OLS analyzation {x_column_name} and {y_column_name}</h3>')
              self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">OLS analyzation {x_column_name} and {y_column_name}</a></li>')
              self.write_record('<p>This record is used by automatically removed Nan data.</p>')
              self.write_record('<pre><code>')
              str_ols_result = self.ols_record(x_column_name, y_column_name)
              self.write_record(f'{str_ols_result}')
              self.write_record('</code></pre>')

              # scatter plot with categorized data
              for category_column in list_category_columns:
                self.write_record(f'<h3 id = {self.id_count()}>Categorized scatter plot {x_column_name} and {y_column_name}</h3>')
                self.list_aside.append(f'<li><a class= "list3" href = "#{self.id}">Categorized scatter plot {x_column_name} and {y_column_name}</a></li>')
                categorized_scatter_path = self.categorical_scatter_plot(x_column_name, y_column_name, category_column)
                categorized_scatter_path = "." + categorized_scatter_path[categorized_scatter_path.rfind('\\'):]
                self.write_record(f'<a href="{categorized_scatter_path}"><img alt="" src="{categorized_scatter_path}" /></a>')
              ##E for
            ##E if
          ##E for ycolum
        ##E for xcolumn
      ##E for csv
    ##E if csv True
  ##E def

  def analyze_data_structure(self, dataframe):
    df = dataframe
    print ("start analyze_data")
    for column_name in df.columns:
      str_dtype = df[column_name].dtype

      if "int" in str(str_dtype):
        self.int_analyzer(column_name, df[column_name])
        ## ???????????????

      elif "float" in str(str_dtype):
        self.float_analyzer(column_name, df[column_name])
        ## ???????????????

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

  ### Make graph
  def heat_map(self, list_num_columns) -> str:
    fig, ax = plt.subplots(1,1, dpi = 300)
    ax = sns.heatmap(data = self.df[list_num_columns].corr(), annot= True)
    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + "heatmap.png")
    fig.savefig(file_path)
    plt.close()
    return file_path

  def hist_plot(self, column_name):
    fig, (ax1, ax2) = plt.subplots(1,2, figsize = (20, 10))
    sns.histplot(data = self.df, x = column_name, kde = True, ax = ax1)
    sm.qqplot(self.df[column_name].values, ax=ax2)

    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + column_name + "-" + "Q-Q_plot.png")
    ax1.set_title("Histgram of " + column_name)
    ax2.set_title("Q-Q plot of " + column_name)
    fig.savefig(file_path)
    plt.close()
    return file_path

  def scatter_plot(self,x_column, y_column)->list:
    fig, ax = plt.subplots(1, 1,dpi = 300)
    ax = sns.scatterplot(data = self.df , x = x_column, y=y_column)
    ax.set_title(x_column + " vs " + y_column)
    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + x_column + "_vs_" + y_column + "-" + "scatterplot.png")
    fig.savefig(file_path)
    plt.close()
    return file_path


  def categorical_hist_plot(self,x_column, category_column):
    fig, ax = plt.subplots(1,1,dpi=300)
    sns.histplot(data = self.df, x = x_column, hue=category_column, alpha = 0.3 , kde = True, ax = ax)
    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + x_column + "-"+ category_column + "categorizedhistplot.png")
    ax.set_title("Histgram of " + x_column + " with " + category_column )
    fig.savefig(file_path)
    plt.close()
    return file_path

  def violin_plot(self, x_column, category_column):
    fig, ax = plt.subplots(1,1,dpi=300)
    sns.violinplot(data = self.df, y = x_column, x=category_column, bw=.2, cut=1,alpha = 0.3 , ax = ax)
    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + x_column + "-"+ category_column + "violinplot.png")
    ax.set_title("Violinplot of " + x_column + " with " + category_column )
    fig.savefig(file_path)
    plt.close()
    return file_path

  def categorical_scatter_plot(self,x_column, y_column, category_column):
    fig, ax = plt.subplots(1, 1,dpi = 300)
    ax = sns.scatterplot(data = self.df , x = x_column, y=y_column,  hue=category_column)
    ax.set_title("Category scatter " + x_column + "categorized by " + category_column)
    file_path = os.path.join(self.create_folder_path, self.csv_name + "-" + x_column +"-" + y_column +"-"+ category_column +"categorized_scatter.png")
    fig.savefig(file_path)
    plt.close()
    return file_path

  # Statistical Analyze
  def ols_record(self, x_column, y_column ):
    df_freena = self.df.dropna()
    model = sm.OLS(df_freena[y_column] ,df_freena[x_column])
    res = model.fit()
    return str(res.summary())

  def one_way_anova(self,category_column, y_column ):
    df_freena = self.df.dropna()
    list_df_series = []
    [list_df_series.append(df_freena[y_column][df_freena[category_column]== for_category_column]) for for_category_column in df_freena[category_column].unique() ]
    f, p = f_oneway(*list_df_series) # list unpack
    return f,p


  def __del__(self):
    self.write_record('</main>')
    self.list_aside.append("</ul>")
    self.list_aside.append("</aside>")
    for write_html in self.list_aside:
      self.write_record(write_html)

    self.write_record('</body>')
    self.write_record('</html>')

if __name__ =="__main__":
  BA = BasicAnalyze()
  BA.analyze(csv_files = [r".\test_train.csv"])
  del BA

