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
    f.write("stocks = ") 
    f.write(str(symbol_dict))


source = join('.','resources','StockList.py')
dest = join('.','lambdas')

# Copy the StockList file to the lambda folders
#    Excluding the root folder
for x in walk(dest)[1:]:
    # Destination file name
    tmp_dest = join(x[0], 'StockList.py')

    # Copy Stocklist file to destination folder
    shutil.copyfile(source, tmp_dest)
