import csv
import sys
import fiona
from collections import defaultdict
import progressbar

# for each field in the shapefile, find the column in the CSV that has
# the most overlapping values

def build_fields(filename, silent=False):
    """
    build a dict containing all values of each field in the shapefile
    """
    fields = {}

    with fiona.open(filename, 'r') as shp_src:    
        for shp in shp_src:                        
            for (shape_field_key, shape_field_value) in shp['properties'].items():                                
                if not shape_field_key in fields:
                    fields[shape_field_key] = {}
                if shape_field_value in (None, ''):
                    continue
                fields[shape_field_key][shape_field_value] = True

    # only record distinct values to make lookup faster
    for field in fields:
        fields[field] = fields[field].keys()
    
    return fields

if __name__ == '__main__':

    print('Building Shapefile comparison table...')
    
    fields = build_fields(sys.argv[2])

    print('Reading CSV...')

    counts = {}

    total_lines = sum(1 for line in open(sys.argv[1], 'r'))
    progress = progressbar.ProgressBar(maxval=total_lines)
    progress.start()

    with open(sys.argv[1], 'r') as csv_src:
        count = 0
        for row in csv.reader(csv_src):
            
            # update progress bar
            count += 1
            progress.update(count)

            # step over each cell in the row
            for (i, row_cell_value) in enumerate(row):                
                
                # check it against each collection of shapefile field values
                for shape_field_key in fields:
                    
                    # skip empty values
                    if row_cell_value in ('', None):
                        continue

                    # tally matches per column
                    if row_cell_value in fields[shape_field_key]:  
                        if ('column_' + str(i)) not in counts:
                            counts['column_' + str(i)] = defaultdict(int) # avoid int/str confusion on integer keys

                        counts['column_' + str(i)][shape_field_key] += 1                            
                        
    progress.finish()

    print("\nMapping from CSV column to Shapefile fields")
    for column in sorted(counts):
        matches = ", ".join(list(map(lambda x: "{key} ({total:.2%})".format(key=x[0], total=x[1]/(total_lines*1.0)), sorted(counts[column].items(), key=lambda x: x[1], reverse=True))))
        print('{column_index}: {matches}'.format(column_index=column.replace('column_',''), matches=matches))



