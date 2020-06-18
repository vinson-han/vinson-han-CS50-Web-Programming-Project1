import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_table():
    commands = (
        ('Create Table loginId('
        'id Serial PRIMARY KEY,'
        'email VARCHAR NOT NULL,' 
        'userName VARCHAR (50) UNIQUE NOT NULL,'
        'password VARCHAR NOT NULL)'),
        
        ('Create Table book('
        'isbn VARCHAR PRIMARY KEY,'
        'title VARCHAR NOT NULL,'
        'author VARCHAR NOT NULL,'
        'year SMALLINT NOT NULL)'),

        ('Create Table rating ('
        'review_id Serial Primary Key,'
        'review VARCHAR NOT NULL,'
        'rating SMALLINT NOT NULL,'
        'review_date DATE NOT NULL,'
        'book_id VARCHAR NOT NULL, FOREIGN KEY(book_id) REFERENCES book(isbn),'
        'username varchar NOT NULL)')
        )


    for command in commands:
        db.execute(command)
   
    db.commit()


if __name__ == '__main__':
    create_table()
