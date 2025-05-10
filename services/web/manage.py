from flask.cli import FlaskGroup

from project import app, db, User


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("seed_db")
def seed_db():
    db.session.add(User(email="michael@mherman.org"))
    db.session.add(User(email="vi6rup9q2t@gmail.com"))
    db.session.add(User(email="pk13a9jm5j@gmail.com"))
    db.session.add(User(email="df9woad4mw@example.com"))
    db.session.add(User(email="53ka53bxy1@gmail.com"))
    db.session.add(User(email="k3yp7hfzt7@outlook.com"))
    db.session.add(User(email="m2fwqnqpqv@gmail.com"))
    db.session.add(User(email="6nlmhkydot@example.com"))
    db.session.add(User(email="yoq7yw8pfk@gmail.com"))
    db.session.add(User(email="n983sp0ptm@yahoo.com"))
    db.session.add(User(email="5jmr337xc1@test.com"))
    db.session.add(User(email="9i1w4lmf52@example.com"))
    db.session.add(User(email="vg6qbp16jn@test.com"))
    db.session.add(User(email="2ddddvf96i@outlook.com"))
    db.session.add(User(email="87a7813jqz@outlook.com"))
    db.session.add(User(email="buuaetyouh@test.com"))
    db.session.add(User(email="gj8n8ep8r0@gmail.com"))
    db.session.add(User(email="ijm8j47byi@example.com"))
    db.session.add(User(email="maps6x08zz@yahoo.com"))
    db.session.add(User(email="fdep7ngxzg@example.com"))
    db.session.add(User(email="figfpfhz7z@outlook.com"))
    db.session.add(User(email="37whjona9m@outlook.com"))
    db.session.add(User(email="11jfntzdjb@example.com"))
    db.session.add(User(email="jw0f9h05to@test.com"))
    db.session.add(User(email="58sc21lngc@test.com"))
    db.session.add(User(email="wxbjgvxdax@example.com"))
    db.session.add(User(email="kbnakla4t0@test.com"))
    db.session.add(User(email="9emrgell0w@test.com"))
    db.session.add(User(email="105316bi79@gmail.com"))
    db.session.add(User(email="7c0d8qx0et@test.com"))
    db.session.add(User(email="leq21flxkw@gmail.com"))
    db.session.add(User(email="g8cx6iggsw@example.com"))
    db.session.add(User(email="98u9rg3o06@outlook.com"))
    db.session.add(User(email="jj3rbbtia4@gmail.com"))
    db.session.add(User(email="ozy74nxtbq@example.com"))
    db.session.add(User(email="6g6zj3m3z8@example.com"))
    db.session.add(User(email="gaymwd9zla@test.com"))
    db.session.add(User(email="xi442471et@gmail.com"))
    db.session.add(User(email="jyo9w6covo@gmail.com"))
    db.session.add(User(email="vy3k6aprgz@outlook.com"))
    db.session.add(User(email="2nrt17i6dz@test.com"))
    db.session.add(User(email="ifb17tolw3@example.com"))
    db.session.add(User(email="8pst56c1nf@yahoo.com"))
    db.session.add(User(email="bnmzlgbyc3@gmail.com"))
    db.session.add(User(email="xpz1dlq445@test.com"))
    db.session.add(User(email="gsyuyhkjur@yahoo.com"))
    db.session.add(User(email="139qlpqwy7@yahoo.com"))
    db.session.add(User(email="anjpx18nrq@example.com"))
    db.session.add(User(email="htrq2pqha7@outlook.com"))
    db.session.add(User(email="57gw7n7o26@example.com"))
    db.session.add(User(email="vuuct6ydox@outlook.com")) 
    db.session.commit()


if __name__ == "__main__":
    cli()
