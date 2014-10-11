import sys
import fiona
import csv

# there must be a pythonic way to do this but I'm seeing weird behavior with
# basic operators. let's be sure!
# def lists_are_same(x, y):
#     if len(x)!=len(y):
#         return False
#     for (i, v) in enumerate(x):
#         if v != y[i]:
#             return False
#     return True

def shape_properties_mismatches(shape_ordered_dict, canonical_row_list):
    # examine all values in the shape except `N03_007`, which should not exist
    # in the canonical admin district row
    mismatched_keys = {}
    for (i, (key, value)) in enumerate(shape_ordered_dict.items()):
        
        if key == 'N03_007':
            continue

        if value != canonical_row_list[i]:
            mismatched_keys[key] = (canonical_row_list[i], value)

    return mismatched_keys


if __name__ == '__main__':
        
    admin_district_details = {}
    with open(sys.argv[1], 'r') as admin_district_src:
        for row in csv.reader(admin_district_src):
            for (i, val) in enumerate(row):
                if val == '':
                    row[i] = None
            admin_district_details[row[-1]] = row[:-1]        

    problematic_admin_districts = {}

    # iterate through all polygons in the shapefile. for each one assigned to a particular 
    # administrative district ID, ensure that each polygon's fields contain identical data
    with fiona.open(sys.argv[2], 'r') as src:   
        for shp in src:
            
            shape_row = [x[1] for x in shp['properties'].items()]
            admin_district_key = shape_row[-1]
            
            # don't try to look up records that don't belong to any admin boundary, 
            # it can only lead to heartbreak
            if admin_district_key is None:
                continue

            # compare the contents of each shape's field to the canonical row for that admin boundary
            shape_row_content = shape_row[:-1]
            canonical_row = admin_district_details[shape_row[-1]]

            mismatches = shape_properties_mismatches(shp['properties'], canonical_row)        
            if len(mismatches)>0:
                if not admin_district_key in problematic_admin_districts:
                    problematic_admin_districts[admin_district_key] = []
                problematic_admin_districts[admin_district_key].append(mismatches)
                
    print("Admin district keys with non-uniform subrecords:")
    print(",".join(problematic_admin_districts.keys()))
    print("")

    for (admin_district_key, mismatches) in problematic_admin_districts.items():
        print("{admin_district_key} mismatches:".format(admin_district_key=admin_district_key))
        print("-----------------")
        for mismatch in mismatches:
            for (problem_element_key, problem_element_value) in mismatch.items():
                print(problem_element_key, problem_element_value)
        print("")


