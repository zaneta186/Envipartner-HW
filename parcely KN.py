import requests, zipfile, io, dbf, csv
from osgeo import ogr
from xml.dom import minidom


# parcely katastralniho uzemi obce Stoky
URL = "http://services.cuzk.cz/shp/ku/epsg-5514/764051.zip"


# download, save and unzip file
r = requests.get(URL)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()


# count of unique polygons
with dbf.Table("764051/PARCELY_KN_P.dbf") as dbs:
    dbf.export(dbs, "PARCELY_KN_P.csv")

with open("PARCELY_KN_P.csv", "r") as table:
    count = len(table.readlines())
    kn = count - 1  # header of table


# convert layer of shp to geometry and extract the area
shp = ogr.Open("764051/PARCELY_KN_P.shp")
layer = shp.GetLayer(0)
areas = []
for feature in layer:
    geom = feature.GetGeometryRef()
    area = geom.GetArea()
    areas.append(area)
average_area = sum(areas) / kn


# creat new csv file for statistics >> total count of unique polygons; average area of polygons
data = [{'TOTAL_COUNT': kn, 'AREA': average_area}]

with open("stat.csv", "w") as statistics:
    fields = ['TOTAL_COUNT', 'AREA']
    writer = csv.DictWriter(statistics, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)

statistics.close()
