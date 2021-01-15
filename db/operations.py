import os
import requests
from db.model import GreenTaxi
from db import postgres_engine, postgres_session
from util import cast_as
from util.config import config
from datetime import datetime


class Operations:
    @staticmethod
    def get_taxi_data(year, month):
        """
        Get taxi data from nyc-tlc site for given year and month.
        :param year: Year of taxi data
        :param month: Month of taxi data
        :return: return path of downloaded csv file
        :rtype: str
        """

        url = f'https://s3.amazonaws.com/nyc-tlc/trip+data/green_tripdata_{year}-{month}.csv'
        r = requests.get(url, stream=True)
        fname = f'data/green_tripdata_{year}-{month}.csv'
        open(fname, 'wb').write(r.content)

        return fname

    @staticmethod
    def get_all_data():
        """
        :return: green taxi data
        :rtype: dict
        """
        session = postgres_session(config.postgres_db)

        try:
            results = session.query(GreenTaxi).all()
            return [r._asdict() for r in results]
        finally:
            session.close()

    @staticmethod
    def write(path, year, month):
        """
        Insert green taxi records to db, then remove csv file.

        :param str path: Path of file to write
        :param year: Year of taxi data
        :param month: Month of taxi data
        """
        print(f'Start time for year:{year} and month:{month} is: {datetime.now()}')
        gt = GreenTaxi
        engine = postgres_engine(config.postgres_db)
        conn = engine.connect()

        try:
            with open(path, 'r') as f:
                next(f)
                entries = []
                for num, line in enumerate(f):
                    header = gt.__table__.columns.keys()
                    row = line.replace('\n', '').split(',')
                    row = [None if len(r) == 0 else r for r in row]
                    item = {
                        header[0]: cast_as(f'{year[2:]}{month}{num}', int),
                        header[1]: cast_as(row[0], int),
                        header[2]: row[1],
                        header[3]: row[2],
                        header[4]: row[3],
                        header[5]: cast_as(row[4], int),
                        header[6]: cast_as(row[5], int),
                        header[7]: cast_as(row[6], int),
                        header[8]: cast_as(row[7], int),
                        header[9]: cast_as(row[8], float),
                        header[10]: cast_as(row[9], float),
                        header[11]: cast_as(row[10], float),
                        header[12]: cast_as(row[11], float),
                        header[13]: cast_as(row[12], float),
                        header[14]: cast_as(row[13], float),
                        header[15]: cast_as(row[14], float),
                        header[16]: cast_as(row[15], float),
                        header[17]: cast_as(row[16], float),
                        header[18]: cast_as(row[17], int),
                        header[19]: cast_as(row[18], int),
                        header[20]: cast_as(row[19], float),
                    }
                    entries.append(item)
            size = 150000
            for entry in (entries[pos:pos + size] for pos in range(0, len(entries), size)):
                conn.execute(gt.__table__.insert(), entry)

        finally:
            conn.close()
            os.remove(path)
