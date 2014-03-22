#!/usr/bin/env python3.3
""" file for executing little fixes to the database """

from database.models import Repository

def fix_repos(session):
    reps=session.query(Repository).all()
    for rep in reps:
        if rep.path[2]==':' and rep.path[0]=='/':
            rep.path=rep.path[1:]
            session.commit()


def main():
    from sqlalchemy.orm import Session
    from database.engines import engine
    session=Session(engine)
    print('Connected to:',engine.url.database)

    fix_repos(session)


if __name__ == '__main__':
    main()

