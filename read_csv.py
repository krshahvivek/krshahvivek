import pandas as pd
import datatable as dt
from dask import dataframe as dd 


"""
read csv
"""
file = "csv_file/web2.csv"

# panda read csv
panda_data_read  = pd.read_csv(file)

#dask dataframe
dask_data_read = dd.read_csv(file)
dask_data_read = dask_data_read.compute()

#datatable # as we go for millions of row datatable is very fast not for the millions of table even for lesser
datatable_data_read = dt.fread(file)
datatable_data_read = datatable_data_read.to_pandas()

""" save csv """
#panda to save csv 
panda_data_read.to_csv(file)

#dash dataframe to save csv
dask_data_read = dd.from_pandas(df,npartitions=1)
dask_data_read.to_csv(file)

#datatable always use this
datatable_data_read = dt.Frame(df)
datatable_data_read.to_csv(file)


'''We don't need Excel or CSV. I Prefer formats like Parquet, Feather, or Pickle to store any DataFrames to.'''