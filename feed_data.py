from db import Base, postgres_engine
from db.operations import Operations
from util import parse_args
from util.config import config


def main():
    args = parse_args()
    year = args.get('year')
    month = args.get('month')
    create_table = args.get('create_table')

    if create_table:
        Base.metadata.create_all(postgres_engine(config.postgres_db))

    op = Operations()
    fname = op.get_taxi_data(year=year, month=month)
    op.write(path=fname, year=year, month=month)


if __name__ == '__main__':
    main()
