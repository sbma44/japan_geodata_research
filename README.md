Requirements
------------
- Python 3
- `make`

Installation
------------
Run `make all` to fetch the necessary data files for this analysis.

You must also install the requisite Python packages listed in requirements.txt. The following will create a virtualenv and perform the installation automatically

```
mkvirtualenv -p `which python3` japan_mlit_post && pip install -r requirements.txt
```

The Shapefile
-------------
The shapefile from the Japanese Ministry of Land, Infrastructure, Transport and Tourism (MLIT) agency contains ~79,000 polygons and has five data fields. Here is an example polygon record:

```
OGRFeature(N03-14_140401):27800
  N03_001 (String) = 静岡県
  N03_002 (String) = (null)
  N03_003 (String) = (null)
  N03_004 (String) = 焼津市
  N03_007 (String) = 22212
```

`N03_007` is always numeric and occurs in long, numerically continuous blocks of records, with considerable contiguity between the other fields. It seems to be an identifier that connects polygons into administrative boundaries. For instance, there are 55 polygons sharing the `N03_007` value `22222`. They render together like so:

![geographic uniformity for 22222](http://cl.ly/image/0x462I0B2M08/Image%202014-10-09%20at%205.41.20%20PM.png)

My working theory was that component polygons did not contain distinct pieces of information and could be considered monolithically. Let's test that.

Generating a CSV of Admin Boundary Field Data
---------------------------------------------
`shp_to_csv.py <shapefile>` walks through the shapefile and, for each distinct `N03_007` value, records the values of the other shapefile fields for first polygon it finds. Simple.

Checking Data Uniformity Within a Hypothetical Admin Boundary
-------------------------------------------------------------
But we'd better test that the first such polygon contains the same data as the others sharing the same `N03_007` value. `check_that_data_is_uniform.py <csv> <shapefile>` iterates through the shapefile, checking that the contents of each polygon's features are identical to the ones recorded in the CSV.

It turns out that they are, except for `N03_007`==`24543`. Hmm.

![only one area with nonuniform data](http://cl.ly/image/0p423y132113/Image%202014-10-09%20at%205.34.12%20PM.png)

The polygons grouped under `24543` have varying `N03_004` values, notably including `所属未定地`.  Google translates this to "Undecided belongs to" and a search identifies some English language near it on the web as "affiliation undecided". I suspect these are just a weird edge case relating to one particular boundary and can be ignored.

Further, the mismatch is specifically between `紀北町` and `紀北町入会地` -- note that one is a substring of the other. More evidence that this is classifying 110 polygons that have a unique administrative status.

Mapping Fields Between Shapefile & Post Code CSV
------------------------------------------------
Feeling confident about `N03_007`'s central role in grouping geometry, let's try to map those administrative boundaries to the post code CSV. `match_fields.py` does the following:

1. Builds a list of unique values for each shapefile field (e.g. `N03_004` contains "`x`, `y` and `z`").
2. Iterates through each row of an input CSV.
3. For each column in that row, check if the value exists in one of the shapefile fields. Record any connections.
4. Print summary statistics displaying the percentage of links between CSV columns and Shapefile fields.

Sanity checking the output of `shp_to_csv.py` against the source Shapefile from which it was created produces:

```
$ python match_fields.py N03-14_140401/N03-14_140401.csv N03-14_140401/N03-14_140401.shp
Building Shapefile comparison table...
Reading CSV...
100% |########################################################################|

Mapping from CSV column to Shapefile fields
0: N03_001 (100.00%)
1: N03_002 (10.05%)
2: N03_003 (58.97%), N03_004 (0.16%)
3: N03_004 (98.79%), N03_003 (1.16%)
4: N03_007 (99.95%)
```

Not bad! These would all be 100%, except that empty values (None, "") are not counted as matches to avoid false positives. `N03_002` and `N03_003` are characterized by large blocks of empty values, so this looks pretty good.

Running the script against one of the Japan Post CSVs yields:

```
$ python match_fields.py postcodes/kogaki.utf8.csv N03-14_140401/N03-14_140401.shp
Building Shapefile comparison table...
Reading CSV...
100% |########################################################################|

Mapping from CSV column to Shapefile fields
0: N03_007 (100.00%)
1: N03_007 (0.87%)
6: N03_001 (100.00%)
7: N03_004 (66.16%), N03_003 (2.45%)
8: N03_004 (1.38%), N03_003 (0.00%)
```

Similar results are obtained from postcodes/oogaki.csv, an alternate-format version of the CSV provided by Japan post, which seems to be related to different systems of kanji spelling/grammar. Whatever the difference between these representation styles is, it doesn't matter for our purposes. 

This is all promising, but let's make sure it isn't a phantom result from easily-matched numeric data like bit flags. The post code CSV looks like this:

>01101,"060  ","0600042","ﾎﾂｶｲﾄﾞｳ","ｻﾂﾎﾟﾛｼﾁﾕｳｵｳｸ","ｵｵﾄﾞｵﾘﾆｼ(1-19ﾁﾖｳﾒ)","北海道","札幌市中央区","大通西（１〜１９丁目）",1,0,1,0,0,0
>01101,"060  ","0600032","ﾎﾂｶｲﾄﾞｳ","ｻﾂﾎﾟﾛｼﾁﾕｳｵｳｸ","ｷﾀ2ｼﾞﾖｳﾋｶﾞｼ","北海道","札幌市中央区","北二条東",0,0,1,0,0,0

Let's be sure we aren't just matching those short numeric fields. Here's a slice of the best-matching columns. (Note that column values are offset by one for the `csvkit` suite of tools, which don't believe in zero-indexing.)

```
$ csvcut -c 1,7,8 postcodes/oogaki.utf8.csv | tail -n 10

47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47381,沖縄県,八重山郡竹富町
47382,沖縄県,八重山郡与那国町
47382,沖縄県,八重山郡与那国町
```

This is good. Column 0 of the postal code CSV matches a value in field `N03_007` -- the field used to group polygons into administrative districts -- 100% of the time. 

Further confirmation can be achieved by spot-checking individual lines from the above. I used this command:

```
$ csvcut -c 1,7,8 postcodes/oogaki.utf8.csv | head -n 123456  |tail -n 1
```

Where `123456` is any number less than 123712 (the number of lines in the postcode CSV). The first column should be used to selectively plot polygons from the shapefile in a tool like QGIS (e.g. "N03_007='47382'"). The second and third columns can be checked against a commercial web mapping service's geocoder. Although doing this exhaustively would be difficult, the results I got were very good.

Conclusions
-----------
The MLIT Shapefile's `N03_007` field is used to group polygons into administrative districts. Column 0 of the Japan Post zipcode CSV uses the same values. Geometry from the shapefile can be associated with string values in the CSV with the following levels of confidence:

- Columns 6 and 7 appear in both files frequently and seem to be useful address information. 
- Column 2 seems to be the actual post code, which is [known to be seven digits](http://www.japan-guide.com/forum/quereadisplay.html?0+39509) and is reliably a 7-digit numeric string in the CSV. 
- It seems likely that columns 3, 4, 5 and 8 contain useful Japanese text. They are most likely to be geographic names that exist at a finer granularity than the shapefile boundaries.