from db import Base
from sqlalchemy import Column, FLOAT, Integer, String, TIMESTAMP
from util.config import config


class GreenTaxi(Base):
    __tablename__ = 'green_taxi'
    __table_args__ = {'schema': config.postgres_db.schema}

    VendorID = Column('VendorID', Integer)
    lpep_pickup_datetime = Column('lpep_pickup_datetime', TIMESTAMP)
    lpep_dropoff_datetime = Column('lpep_dropoff_datetime', TIMESTAMP)
    store_and_fwd_flag = Column('store_and_fwd_flag', String(1))
    RatecodeID = Column('RatecodeID', Integer)
    PULocationID = Column('PULocationID', Integer)
    DOLocationID = Column('DOLocationID', Integer)
    passenger_count = Column('passenger_count', Integer)
    trip_distance = Column('trip_distance', FLOAT)
    fare_amount = Column('fare_amount', FLOAT)
    extra = Column('extra', FLOAT)
    mta_tax = Column('mta_tax', FLOAT)
    tip_amount = Column('tip_amount', FLOAT)
    tolls_amount = Column('tolls_amount', FLOAT)
    ehail_fee = Column('ehail_fee', FLOAT)
    improvement_surcharge = Column('improvement_surcharge', FLOAT)
    total_amount = Column('total_amount', FLOAT)
    payment_type = Column('payment_type', Integer)
    trip_type = Column('trip_type', Integer)
    congestion_surcharge = Column('congestion_surcharge', FLOAT)
