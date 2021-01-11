from db.model import GreenTaxi
from db import postgres_session
from util.config import config


class Operations:
    @staticmethod
    def get_all_data():
        """
        :return: green taxi data
        :rtype: dict
        """
        session = postgres_session(config.ds_ozoo)

        try:
            results = session.query(GreenTaxi).all()
            return [r._asdict() for r in results]
        finally:
            session.close()
