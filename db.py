import postgresql

db_address = 'pq://postgres:postgres@localhost:5432/landing'

def dbquery(query):
    with postgresql.open(db_address) as db:
        response = db.query(query)
    return response


def dbexecute(query):
    with postgresql.open(db_address) as db:
        db.execute(query)