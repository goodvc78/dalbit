# -*- coding: utf-8 -*-
import os
import zlib
import time
import errno   
import codecs
import hashlib
import logging
import datetime
from tqdm import tqdm
from configparser import ConfigParser

from utils.db_util import UrlDb


class Extractor:
    def __init__(self):
        self.udb = UrlDb()
        self.load_config()
        self.set_logger()
        pass

    def load_config(self, fname='./config/extractor.conf'):
        self.config = ConfigParser()
        self.config.read(fname)

    def set_logger(self):
        self.logger = logging.getLogger('extractor')
        logging.basicConfig(level=self.config['logging']['level'], 
                format="[%(asctime)s %(levelname)s:%(name)s] %(message)s")

    def read_urldb(self, start_idx, end_idx):
        q = '''
        select *
        from dalbit_urldb 
        where id between {start_idx} and {end_idx} 
        '''.format(start_idx=start_idx, end_idx=end_idx)

        url_ds = self.udb.execute_select(q)
        return url_ds

    def fetch_data(self, q, out_fname, salt, delimiter=u',', fetch_size=10):
        def hashing(row):
            hashed = self.to_hash(row.get('host', ''), salt)
            row['host'] = hashed

        def _write_row(f, row):
            row = map(str, row)
            s = delimiter.join(row)
            f.write(s)
            f.write('\n')
      
        with self.udb.db_con.cursor() as cursor:
            cursor.execute(q)
            fout = codecs.open(out_fname, 'w', 'utf-8')
            header = [desc[0] for desc in cursor.description]
            _write_row(fout, header)
            n_rows = 0
            pbar = tqdm()
            max_idx, min_idx = 0, 2147483647

            while True:
                rows = cursor.fetchmany(fetch_size)
                if not rows:
                    break
                for row in rows:
                    max_idx = max(max_idx, row['id'])
                    min_idx = min(min_idx, row['id'])
                    hashing(row)
                    row = [row.get(col, '') for col in header]
                    _write_row(fout, row)
                    n_rows += 1
                pbar.update(len(rows))

            fout.close()
            pbar.close()
        return (n_rows, min_idx, max_idx)

    def get_last_ver(self, type='part'):
        conditions = ''
        if type!='part':
            conditions = " where file_type = 'full' "
        q = '''
        select file_ver, start_idx, end_idx, reg_date 
        from dalbit_checkpoint 
        {conditions}
        order by id desc 
        limit 1 
        '''.format(conditions=conditions)

        r = self.udb.execute_select(q, output_pandas=False)
        if len(r) < 1:
            raise Exception('Version checkpoint is empty : %s(%s)  / sql = %s' % (type, r, q))

        return r[0]

    def increase_ver(self, ver, type='part'):
        pos = 2 if 'part' in type else 1
        tkns = ver.split('.', 3)
        tkns[pos] = str(int(tkns[pos])+1)
        if 'full' in type:
            tkns[2] = '0'
        return '.'.join(tkns)

    def to_hash(self, data, salt):
        s = '{salt}.{data}'.format(salt=salt, data=data)
        h = hashlib.sha256()
        h.update(s.encode())
        r = h.digest()
        return r.hex()

    def gen_salt_key(self, string, prefix='dalbit', init_val=1218):
        # truncate micro version 
        string = string.rsplit('.', 1)[0]
        s = '%s.%s' % (prefix, zlib.crc32(string.encode(), 1218))
        r = self.to_hash(s, prefix)
        r = zlib.crc32(r.encode(), 1218)
        return '%x' % r

    def add_new_ver(self, ver, type, salt, start_idx, end_idx, n_affected):
        # TODO : The new version must be greater than the last version
        
        q = '''
        insert into dalbit_checkpoint(file_type, file_ver, salt_key, start_idx, end_idx, affected_rows, file_path, reg_date)
        values('{type}', '{ver}', '{salt}', {start_idx}, {end_idx}, {rows}, 'dalbit.{type}.{ver}.csv', NOW())
        '''.format(type=type, ver=ver, salt=salt, start_idx=start_idx, end_idx=end_idx, rows=n_affected)
        n = self.udb.execute_cud(q)
        return n

    def _get_urldb_rows(self, start_idx):
        q = '''
        select count(1) n_row from dalbit_urldb du where id > {idx}
        '''.format(idx=start_idx)
        r = self.udb.execute_select(q, output_pandas=False)[0]
        return r['n_row']

    def _check_versioning(self, t, min_count, min_period):
        '''
        check for new versioning
        ------

        type : version type 'part' or 'full'
        min_count : Minium unsaved UrlDB quantity for versioning
        min_perid : Minium unsaved UrlDB period(minute) for versioning 
        '''
        last_ver = self.get_last_ver(t)
        remains = self._get_urldb_rows(last_ver['end_idx'])
        elapsed = (datetime.datetime.now() - last_ver['reg_date']).total_seconds() / 60
        if remains == 0:
            return False

        if remains > min_count:
            return True


        if int(elapsed) > int(min_period):
            return True

        return False

    def _make_url_query(self, start_idx, end_idx=-1):
        end_condition = '' if end_idx == -1 else ' and id <= %s' % end_idx
        q = '''
        select id, gtype, gid, pid, cate_desc, dtype, host, path
        from dalbit_urldb
        where id > {start_idx} {end_condition}
        '''.format(start_idx=start_idx, end_condition=end_condition)
        return q

    def _make_out_fname(self, ver, type):
        '''
        version : example full.0001.0.0.10
        '''
        home = self.config['output']['home_dir']
        tkns = ver.split('.')
        fname = 'dalbit.{type}.{ver}.csv'.format(type=type, ver=ver)
        full_path = os.path.join(home, tkns[-3], tkns[-2], fname)
        return full_path

    def _make_dir(self, path):
        if path[-1] != '/':
            path = path.rsplit('/', 1)[0]
        try:
            os.makedirs(path)
            self.logger.info('Make dir : %s' % path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise        

    def fetch_urlfile(self, start_idx, end_idx, ver, type, salt):
        sql = self._make_url_query(start_idx, end_idx)
        fname = self._make_out_fname(ver, type)
        self._make_dir(fname)
        affected_rows, min_idx, max_idx = self.fetch_data(sql, fname, salt)
  
        self.logger.info('Fetched UrlDb(%s): %d rows(index=%s~%s), %s' % (
            ver, affected_rows, min_idx, max_idx, fname))
        return affected_rows, min_idx, max_idx

    def make_urlfile(self):
        for target in ['minor', 'micro']:
            # check versioning        
            type = 'full' if target == 'minor' else 'part'
            min_count = int(self.config['versioning'][target+'_count'])
            min_period = float(self.config['versioning'][target+'_period'])
            if not self._check_versioning(type, min_count, min_period):
                continue
            
            # fetch urldb data
            last_ver = self.get_last_ver(type)
            new_ver = self.increase_ver(last_ver['file_ver'], type)
            # start_idx = last_ver['end_idx'] if type == 'part' else 0
            
            salt_key = self.gen_salt_key(new_ver)
            # make full version url file
            n, min_idx, max_idx = self.fetch_urlfile(0, -1, new_ver, 'full', salt_key)
            r = self.add_new_ver(new_ver, 'full', salt_key, min_idx, max_idx, n)
            # make part version url file 
            n, min_idx, max_idx = self.fetch_urlfile(last_ver['end_idx'], -1, new_ver, 'part', salt_key)
            r = self.add_new_ver(new_ver, 'part', salt_key, min_idx, max_idx, n)
            
            if not r:
                self.logger.warning('Failed add new version(%s) : sql - %s' % (ver, q))
                continue
            self.logger.info('Add new version : %s-%s (%s rows/index %d~%d)' % (target, new_ver, n, min_idx, max_idx))

    def run(self):
        while(1):
            tick = time.time()
            self.load_config()
            self.make_urlfile()
            sleep_time = int(self.config['versioning']['check_period'])
            if (time.time() - tick) < sleep_time:
                self.logger.info('Wait %s seconds for next version check' % sleep_time)  
                time.sleep(sleep_time)


if __name__ == "__main__":
    import fire
    e = Extractor()
    fire.Fire({
        'run': e.run
    })

    
