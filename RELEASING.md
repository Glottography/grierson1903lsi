# Releasing the dataset

In case of upstream changes in glottography-data:
```shell
cldfbench download cldfbench_grierson1903lsi.py
```

## Recreate the CLDF data

```shell
cldfbench makecldf cldfbench_grierson1903lsi.py --glottolog-version v5.2
cldfbench cldfreadme cldfbench_grierson1903lsi.py
cldfbench zenodo --communities glottography cldfbench_grierson1903lsi.py
cldfbench readme cldfbench_grierson1903lsi.py
```

## Validation

```shell
cldf validate cldf
```

```shell
cldfbench geojson.validate cldf
```

```shell
cldfbench geojson.glottolog_distance cldf --format tsv | csvformat -t | csvgrep -c Distance -r"^0\.?" -i | csvsort -c Distance | csvcut -c ID,Distance | csvformat -E | termgraph
```

```shell
rang1266: ▇▇▇▇▇▇▇▇▇▇▇▇ 1.03 
amri1238: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 1.21 
kuru1301: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 1.33 
aito1238: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 1.56 
west2386: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 1.88 
asur1254: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.17 
hind1269: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.65 
bagh1251: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 4.05 
```