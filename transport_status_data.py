from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("postgresql+psycopg2://postgres:@localhost/postgres")

Base = declarative_base()
Session = sessionmaker(bind=engine)


class FullNames(Base):
    __tablename__ = 'full_names'
    name = Column(String, primary_key=True, nullable=False)
    status = Column(Integer)


class ShortNames(Base):
    __tablename__ = 'short_names'
    name = Column(String, primary_key=True, nullable=False)
    status = Column(Integer)


def transport_status():
    with Session() as session:
        short_names = session.query(ShortNames).all()
        short_names_dict = {row.name: row.status for row in short_names}
        full_names = session.query(FullNames).all()
        for row in full_names:
            row.status = short_names_dict[row.name.split('.')[0]]
        session.commit()


transport_status()
