import pandas
from os.path import join
from os import walk
import shutil

# Read source CSV File
df = pandas.read_csv( join('.','resources','StockList.csv'))

# Create dict of symbols 
symbol_dict = { row['Symbol'] : row['Description'] for index, row in df.iterrows()}

# Write that dict to file
with open(join('.','resources','StockList.py'), '+w') as f:
    f.write("stocks = {\n") 
    for key, value  in symbol_dict.items():
        f.write(f"\t\"{key}\": \"{value}\",\n")
    f.write("\t}")


source = join('.','resources','StockList.py')
dest = join('.','lambdas')

# Copy the StockList file to the lambda folders
#    Excluding the root folder
for x in walk(dest):
    
    if x[0] == dest:
        continue

    # Destination file name
    tmp_dest = join(x[0], 'StockList.py')

    # Copy Stocklist file to destination folder
    shutil.copyfile(source, tmp_dest)
