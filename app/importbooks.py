import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#export DATABASE_URL=postgres://utghlhxnukoghb:d2c56b981ec9b5e71dcb702cde71369bf5a616f4a01666331f92ac78db608690@ec2-54-217-235-166.eu-west-1.compute.amazonaws.com:5432/d6lo9nlkfrqrtr

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f,delimiter="\t",quotechar="\t",quoting=csv.QUOTE_MINIMAL)

    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn": isbn, "title": title, "author": author, "year": year})
        print("Added %s by %s, written in %s with isbn %s") % (title,author,year,isbn)
        db.commit()

if __name__ == "__main__":
    main()
