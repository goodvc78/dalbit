# -*- coding: utf-8 -*-
import pandas as pd
from tqdm import tqdm
import pymysql.cursors


class UrlDb:
    def __init__(self, host='mysql', 
         user='root', 
		 password='dalbit!@#', 
		 db='urldb',):
        self.db_con = pymysql.connect(
                        host=host,
                        user=user,
                        password=password,
                        db=db,
                        cursorclass=pymysql.cursors.DictCursor)
        self.db_con.autocommit(True)
        
    
    def execute_select(self, sql, output_pandas = True):
        with self.db_con.cursor() as cursor:
            # Read a single record
            cursor.execute(sql)
            rows = cursor.fetchall()
        if output_pandas:
            return pd.DataFrame(list(rows), columns = list(map(lambda x:x[0], cursor.description)))
        return rows
            
    def execute_cud(self, sql):
        with self.db_con.cursor() as cursor:
            # Read a single record
            n = cursor.execute(sql)
            self.db_con.commit()
        return n
    
    def __del__(self):
        self.db_con.close()
    
