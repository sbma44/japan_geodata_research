import sys
import fiona
import csv

writer = csv.writer(sys.stdout)

with fiona.open(sys.argv[1], 'r') as src:
    fields = [x[0] for x in src.schema.get('properties', {}).items()]

    found_admin_boundaries = []

    for shp in src:
        shape_row = [x[1] for x in shp['properties'].items()]

        # many shapes comprise one administrative district. the last field, N03_007, 
        # contains the ID that binds them together. all non-geometry fields will be
        # identical.
        admin_boundary_id = shape_row[-1]
        if admin_boundary_id not in found_admin_boundaries:
            found_admin_boundaries.append(admin_boundary_id)
            writer.writerow(shape_row)