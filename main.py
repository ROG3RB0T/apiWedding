from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, MetaData, Table
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from datetime import datetime

from starlette.responses import JSONResponse

# Database Connection
DATABASE_URL = "postgresql://postgres:c-cCc421acebfGCgedA4fDfF2cCC-44e@viaduct.proxy.rlwy.net:10502/weddingDB"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our SQLAlchemy models
Base = declarative_base()
# Define a SQLAlchemy model
class Item(Base):
    __tablename__ = "rsvp"
    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String, index=True)
    guest_invitation = Column(String, index=True)
    rsvp_spot = Column(Integer)
    rsvp_date = Column(DateTime, index=True)
    rsvp_checkin = Column(Boolean)
    rsvp_status = Column(String,index=True)
    Created_at = Column(DateTime)
    Updated_at = Column(DateTime)

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpoints

@app.post("/rsvp/checkin/{rsvp_id}")
def checkin(rsvp_id: int, db:Session = Depends(get_db)):
    try:
        exist_rsvp = db.query(Item).filter(Item.id == rsvp_id).first()
        if exist_rsvp is None:
            raise HTTPException(status_code=404, detail="No encontrado")

        exist_rsvp.rsvp_checkin = True
        exist_rsvp.rsvp_date = datetime.now()
        exist_rsvp.Updated_at = datetime.now()
        exist_rsvp.rsvp_status = 'Confirmado'
        db.commit()

        return JSONResponse(content={"status":"Confirmado"}, status_code=200);


    except ProgrammingError as e:

        # Handling the ProgrammingError and returning a JSON response

        error_message = f"Database error: {str(e)}"

        return JSONResponse(content={"error": error_message}, status_code=500)


    except Exception as e:

        # Handle other exceptions if needed

        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/rsvp/checkout/{rsvp_id}")
def checkout(rsvp_id: int, db:Session = Depends(get_db)):
    try:
        exist_rsvp = db.query(Item).filter(Item.id == rsvp_id).first()

        if exist_rsvp is None:
            raise HTTPException(status_code=404, detail="No encontrado")

        exist_rsvp.rsvp_checkin = False
        exist_rsvp.updated_at = datetime.now()
        exist_rsvp.rsvp_spot = 0
        exist_rsvp.rsvp_status = 'No Asistencia'
        db.commit()
        return JSONResponse(content={"status":"Cancelada"},status_code=200);

    except ProgrammingError as e:
        error_message = f"Database error: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/rsvp/{item_id}")
async def read_item(item_id: int, db: Session = Depends(get_db)):
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item


    except ProgrammingError as e:
        # Handling the ProgrammingError and returning a JSON response
        error_message = f"Database error: {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)

    except Exception as e:
        # Handle other exceptions if needed
        return JSONResponse(content={"error": str(e)}, status_code=500)