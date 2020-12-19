# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'..')
from datetime import datetime

from utils.db_util import UrlDb

class ImportTool:
    def __init__(self):
        pass

    def load_data(self, path, header=None, formatter=lambda x: x):
        def tokenizer(s):
            return s.strip().split(',')

        with open(path, encoding='utf-8-sig') as fin:
            if not header:
                header = fin.readline()
                header = tokenize(header)
            lines = []
            for line in fin.readlines():
                line = tokenizer(line)
                line = formatter(line)
                if not line:
                    continue
                if len(line) != len(header):
                    continue
                lines.append(line)
        return header, lines

    def make_insert_sql(self, table, header, rows, wrap_cols=[], skip_cols=['id']):
        def wrap_values(vals):
            ret = []
            for idx, val in enumerate(vals):
                if idx in skip_indexes:
                    continue
                ret.append(f'"{val}"' if idx in wrap_indexes else val)
            return ret

        wrap_indexes = {idx for idx, col in enumerate(header) if col in wrap_cols}
        skip_indexes = {idx for idx, col in enumerate(header) if col in skip_cols}
        columns = ','.join([col for col in header if col not in skip_cols])
        val_list = []
        for vals in rows:
            vals = ', '.join(wrap_values(vals))
            val_list.append('(' + vals + ')')
        val_str = ', '.join(val_list)

        q = f'insert into {table} ({columns}) values {val_str} ;'
        return q

    def run_migration_old_urldb(self, fname, fetch_size=100):
        udb = UrlDb()

        header, lines = self.load_data(fname)
        wrap_cols = ['gtype', 'gid', 'gname', 'pid', 
                     'host', 'description', 'reg_date', 
                     'mod_date', 'path']
        skip_cols = ['id']
        affected_rows = 0
        for pos in range(0, len(lines), fetch_size):
            rows = lines[pos:pos+fetch_size]
            q = self.make_insert_sql('dalbit_urldb', header, rows, wrap_cols, skip_cols)
            # affected_rows += udb.execute_cud(q)
            print(f'affected rows : {affected_rows}')

    def load_mig_data(self, fname, desc=''):
        def mig_formatter(vals):
            if len(vals) != 9:
                return None
            url =  vals[5].split('/', 1)
            if len(url) < 2:
                url.append('')
            url[1] = '/' + url[1]
            vals = vals[:5] + url + vals[6:]
            if not vals[8]:
                vals[8] = datetime.now().strftime('%Y%m%d')
            if not vals[9]:
                vals[9] = vals[8]
            vals.append(desc)
            return vals
        header = ['gtype', 'gid', 'pid', 'cate_desc', 
                  'dtype', 'host', 'path', 'tmp', 
                  'reg_date', 'mod_date', 'description']
        header, lines = self.load_data(fname, header=header, formatter=mig_formatter)        
        return header, lines

    def run_migration(self, fname, desc='', fetch_size=1000, limit=None):
        if not desc:
            desc = str(datetime.now())

        udb = UrlDb()
        
        header, lines = self.load_mig_data(fname, desc=desc)
        if limit:
            lines = lines[:limit]
        print(f'Loaded migration data from {fname}')
        
        wrap_cols = ['gtype', 'gid', 'pid', 'cate_desc', 
                     'host', 'path', 'reg_date', 'mod_date', 'description']
        skip_cols = ['tmp']
        
        affected_rows = 0
        print(f'Start importing migration data: desc = {desc}')
        for pos in range(0, len(lines), fetch_size):
            rows = lines[pos:pos+fetch_size]
            q = self.make_insert_sql('dalbit_migration_urldb', header, rows, wrap_cols, skip_cols)
            affected_rows += udb.execute_cud(q)
            print(f'Affected rows : {affected_rows}')
        
        self.delete_duplicated_rows(desc)
        self.insert_migration_data(desc)

    def delete_duplicated_rows(self, description):
        udb = UrlDb()
        q = f'''
        delete
            dalbit_urldb
        from
            dalbit_urldb
        left join dalbit_migration_urldb m on
            dalbit_urldb.host = m.host
            and dalbit_urldb.path = m.path
            and dalbit_urldb.pid = m.pid
        where
            m.description = '{description}';
        '''
        print(q)
        affected_rows = udb.execute_cud(q)
        print(f'Deleted rows : {affected_rows}')

    def insert_migration_data(self, description):
        udb = UrlDb()
        q = f'''
        insert into 
            dalbit_urldb(gtype, gid, pid, host, description, reg_date, mod_date, dtype, path, cate_desc)
        select 
            gtype, gid, pid, host, description, reg_date, mod_date, dtype, path, cate_desc 
        from 
            dalbit_migration_urldb
        where 
            description = '{description}';
        '''
        print(q)
        affected_rows = udb.execute_cud(q)
        print(f'Affected rows : {affected_rows}')


if __name__ == "__main__":
    import fire
    tool = ImportTool()
    fire.Fire({
        'run_mig': tool.run_migration
    })
