import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def import_data():
    with open('books.csv',newline='') as csvfile:
        rows = csv.DictReader(csvfile,delimiter=',')
        #for isbn,title,author,year in rows
        for row in rows:
            isbn = row['isbn']
            title = row['title']
            author = row['author']
            year = int(row['year'])
            db.execute('Insert Into book(isbn,title,author,year) VALUES(:isbn, :title, :author, :year)',
                {'isbn':isbn,'title':title,'author':author,'year':year})
        db.commit()


if __name__ == '__main__':
    import_data()