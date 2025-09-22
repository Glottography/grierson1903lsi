import pathlib
import functools

from csvw.dsv import UnicodeWriter
from cldfgeojson.create import feature_collection
from clldutils.jsonlib import load, dump
import pyglottography


FIX_GLOTTOCODES = {
    'godw1240': 'godw1241',
    'bagh1252': 'bagh1251',
}
PAGES = {
    '1-1': '550',
    '1-2': '381',
    '2': '245',
    '3-1': '670',
    '3-2': '540',
    '3-3': '416',
    '4': '701',
    '5-1': '463',
    '5-2': '466',
    '6': '286',
    '7': '424',
    '8-1': '600',
    '8-2': '584',
    '9-1': '843',
    '9-2': '494',
    '9-3': '338',
    '9-4': '998',
    '10': '567',
}


class Dataset(pyglottography.Dataset):
    dir = pathlib.Path(__file__).parent
    id = "grierson1903lsi"

    @functools.cached_property
    def maps_by_name(self) -> dict:
        return {r['name']: r for r in self.etc_dir.read_csv('maps.csv', dicts=True)}

    def cmd_download(self, args):
        dsal_maps = {v['id']: v for v in self.maps_by_name.values()}
        dsal_maps_by_lldir = {v['LL_MAP_DIR']: v for v in dsal_maps.values()}

        cols = ['NAME', 'FAMCODE', 'SUBGRPCD', 'LANGCODE', 'DIALCODE']
        features = []
        glottocode_map = {
            tuple(r[c] for c in cols): r['Glottocode']
            for r in self.etc_dir.read_csv('geolangs.csv', dicts=True)}
        fid = 0
        for p in sorted(
                list(self.raw_dir.joinpath('geo').glob('*/features.geojson')) + list(self.raw_dir.joinpath('geo', 'dsal_maps').glob('*.geojson')),
                key=lambda p: p.name):
            if p.parent.name in dsal_maps_by_lldir:
                map_name_full = dsal_maps_by_lldir[p.parent.name]['name']
            else:
                map_name_full = dsal_maps[p.stem + '.jpg']['name']
            for f in load(p)['features']:
                if 'glottocode' in f['properties']:
                    gc = FIX_GLOTTOCODES.get(
                        f['properties']['glottocode'].strip(),
                        f['properties']['glottocode'].strip())
                    name = f['properties']['name']
                elif 'Polygon' in f['geometry']['type'] and f['properties']['NAME']:
                    key = tuple(f['properties'].get(col, '') or '' for col in cols)
                    gc = glottocode_map[key]
                    name = f['properties']['NAME']
                else:
                    assert 'Polygon' not in f['geometry']['type'] or f['properties']['NAME'] is None, f['properties']
                    continue

                fid += 1
                props = {
                    'id': str(fid),
                    'name': name,
                    'glottocode': gc,
                    'year': '1903',
                    'map_name_full': map_name_full,  # FIXME: add URL
                }
                f['properties'] = props
                features.append(f)

        dump(feature_collection(features), self.raw_dir / 'dataset.geojson', indent=2)
        cols = ['id', 'name', 'glottocode', 'year', 'map_name_full']
        with UnicodeWriter(self.etc_dir / 'features.csv') as w:
            w.writerow(cols)
            for f in features:
                w.writerow([f['properties'].get(col) for col in cols])

    def local_schema(self, cldf):
        cldf.add_columns('ContributionTable', 'URL')

    def georeferenced_files(self, p):
        if p.is_dir():
            if list(p.glob('*_modified_2.tif')):
                geotiff = list(p.glob('*_modified_2.tif'))[0]
            else:
                geotiff = list(p.glob('*_modified.tif'))[0]
            web = p / 'web.jpg'
        else:  # A geotif in dsal_maps
            geotiff = p
            web = p.parent / '{}.jpg'.format(p.stem.replace('modified', 'web'))
        bounds = web.parent / '{}.bounds.geojson'.format(web.name)
        assert all(pp.exists() for pp in [geotiff, web,bounds])
        return (geotiff, web, bounds)

    def make_contribution_map(self, args, maps, md, **kw):
        res = pyglottography.Dataset.make_contribution_map(self, args, maps, md)
        assert 'LL_MAP_DIR' in md
        if md['LL_MAP_DIR'] and self.raw_dir.joinpath('geo', md['LL_MAP_DIR']).exists():
            geotiff, web, bounds = self.georeferenced_files(
                self.raw_dir.joinpath('geo', md['LL_MAP_DIR']))
        else:
            assert self.raw_dir.joinpath('geo', 'dsal_maps', res['ID'] + '_modified.tif').exists()
            geotiff, web, bounds = self.georeferenced_files(
                self.raw_dir.joinpath('geo', 'dsal_maps', res['ID'] + '_modified.tif'))

        res['Media_IDs'] = []
        for mf in self.iter_map_files(self.cldf_dir, res, geotiff, web, bounds):
            res['Media_IDs'].append(mf['ID'])
            args.writer.objects['MediaTable'].append(mf)

        comps = md['id'].split('-')
        assert comps[0] == 'lsi'
        comps = comps[1:]
        page = comps[-1]
        comps = comps[:-1]
        assert len(comps) in {1, 2}
        vol = '-'.join(comps)
        assert vol.startswith('v')
        vol = vol[1:]
        res['URL'] = ("https://dsal.uchicago.edu/books/lsi/lsi.php?"
                      "volume={}&pages={}#page/{}/mode/1up").format(vol, PAGES[vol], page)
        return res
