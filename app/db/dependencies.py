from app.db.session import SessionLocal

def getDB():
    db = SessionLocal()

    try: 
        yield db
    finally:
        db.close()