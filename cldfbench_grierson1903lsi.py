import pathlib

from csvw.dsv import UnicodeWriter
from cldfgeojson.create import feature_collection
from clldutils.jsonlib import load, dump
import pyglottography


FIX_GLOTTOCODES = {
    'godw1240': 'godw1241',
    'bagh1252': 'bagh1251',
}


class Dataset(pyglottography.Dataset):
    dir = pathlib.Path(__file__).parent
    id = "grierson1903lsi"

    def cmd_download(self, args):
        dsal_maps = {v['DSAL_SCAN']: v for v in self.etc_dir.read_csv('dsalmaps.csv', dicts=True)}
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
                map_name_full = dsal_maps_by_lldir[p.parent.name]['Title']
            else:
                map_name_full = dsal_maps[p.stem + '.jpg']['Title']
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
