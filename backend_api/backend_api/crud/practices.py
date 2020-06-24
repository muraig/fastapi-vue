from sqlalchemy.orm import Session
import sqlalchemy.exc

from backend_api import database_models as tables
from backend_api import pydantic_schemas as schemas
from backend_api.pydantic_schemas import PracticeCreate


def get_practices_all(db: Session, skip, limit):
    return db.query(tables.Practice).offset(skip).limit(limit).all()


def get_practice_by_id(db: Session, practice_id: int):
    return db.query(tables.Practice).filter(tables.Practice.id == practice_id).first()


def get_practice_by_name(db: Session, gp_name: str):
    return db.query(tables.Practice).filter(tables.Practice.name == gp_name).first()


def update_practice(db: Session, updated_practice: PracticeCreate):
    practice = tables.Practice(**updated_practice.dict())

    try:
        db.add(practice)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        practice = get_practice_by_name(db, updated_practice.name)

        practice.phone_num = updated_practice.phone_num
        practice.national_code = updated_practice.national_code
        practice.emis_cdb_practice_code = updated_practice.emis_cdb_practice_code
        practice.go_live_date = updated_practice.go_live_date
        practice.closed = updated_practice.closed
        db.add(practice)
        db.commit()

    db.refresh(practice)
    return practice


def get_addresses_all(db: Session, skip, limit):
    return db.query(tables.Address).offset(skip).limit(limit).all()


def get_address_by_practice_name(db: Session, practice_name: str):
    return get_practice_by_name(db, practice_name).address


def update_address_by_practice_id(db: Session, practice_id: int, new_address: schemas.AddressCreate):
    address: tables.Address = tables.Address(**new_address.dict(), practice_id=practice_id)

    try:
        db.add(address)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        address = db.query(tables.Address).filter(tables.Address.practice_id == practice_id).first()

        address.line_1 = new_address.line_1
        address.line_2 = new_address.line_2
        address.town = new_address.town
        address.county = new_address.county
        address.postcode = new_address.postcode
        address.dts_email = new_address.dts_email

        db.add(address)
        db.commit()

    db.refresh(address)
    return address


def add_access_system(db: Session, new_access_system: schemas.AccessSystemCreate):
    access_system = tables.AccessSystem(**new_access_system.dict())
    db.add(access_system)
    db.commit()
    db.refresh(access_system)
    return access_system


def add_ip_range(db: Session, new_ip_range: schemas.IPRangeCreate):
    ip_range = tables.IPRange(**new_ip_range.dict())
    db.add(ip_range)
    db.commit()
    db.refresh(ip_range)
    return ip_range