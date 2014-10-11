postcodes/kogaki.zip:
	mkdir postcodes
	curl http://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip > ./postcodes/kogaki.zip

postcodes/kogaki.utf8.csv: postcodes/kogaki.zip
	cd postcodes && unzip kogaki.zip
	iconv -f SHIFT_JIS -t UTF-8 ./postcodes/KEN_ALL.CSV > ./postcodes/kogaki.utf8.csv
	rm postcodes/KEN_ALL.CSV postcodes/kogaki.zip

N03-140401_GML.zip:
	curl 'http://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-14/N03-140401_GML.zip' -H 'DNT: 1' -H 'Accept-Encoding: gzip,deflate,sdch' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.101 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Referer: http://nlftp.mlit.go.jp/ksj/gml/cgi-bin/download.php' -H 'Cookie: Mojavi=hluic4q5s4n1jfscvaph1jo6h4; FJNADDSPID=1tgE1a' -H 'Connection: keep-alive' --compressed > N03-140401_GML.zip

N03-140401_GML/N03-14_140401.csv: N03-140401_GML.zip
	unzip N03-140401_GML.zip
	rm N03-140401_GML.zip
	python shp_to_csv.py N03-140401_GML/N03-14_140401.shp > N03-140401_GML/N03-14_140401.csv

all: postcodes/kogaki.utf8.csv N03-140401_GML/N03-14_140401.csv