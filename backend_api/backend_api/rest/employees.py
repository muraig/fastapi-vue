import sqlalchemy.exc
from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import backend_api.exc
import backend_api.pydantic_schemas as schemas
from backend_api.crud import employees as crud_employees
from backend_api.database_connection import get_db_session

# Create a fastapi router for these REST endpoints
router = APIRouter()


# Create a new employee entry
@router.post("/employee", response_model=schemas.Employee)
def add_new_employee(new_employee: schemas.EmployeeCreate, db: Session = Depends(get_db_session)):
    employee = crud_employees.read_employee_by_email(db, new_employee.email)
    if employee:
        raise HTTPException(status_code=400, detail=f"GP Employee with email {new_employee.email} already registered")
    return crud_employees.add_employee(db, new_employee)


# Get multiple/all employees
@router.get("/employees", response_model=List[schemas.Employee])
def get_all_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    employees = crud_employees.read_all_employees(db, skip=skip, limit=limit)
    return employees


# Get employee details using database primary key
@router.get("/employee/id", response_model=schemas.Employee)
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db_session)):
    employee = crud_employees.read_employee_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"No employee found with ID {employee_id}")
    return employee


# Get employee details using email address
@router.get("/employee/email", response_model=schemas.Employee)
def get_employee_by_email(email: str, db: Session = Depends(get_db_session)):
    employee = crud_employees.read_employee_by_email(db, email)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"No employee found with email {email}")
    return employee


# Get employee details using first name
@router.get("/employee/name", response_model=schemas.Employee)
def get_employee_by_name(name: str, db: Session = Depends(get_db_session)):
    employee = crud_employees.read_employee_by_name(db, name)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"No employee found with first name {name}")
    return employee


# Get employee details using professional_num (GMC/NMC number)
@router.get("/employee/professional_num", response_model=schemas.Employee)
def get_employee_by_professional_num(professional_num: str, db: Session = Depends(get_db_session)):
    employee = crud_employees.read_employee_by_professional_num(db, professional_num)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"No employee found with professional num {professional_num}")
    return employee


# Modify details for existing employee entry
@router.put("/employee", response_model=schemas.Employee)
def modify_existing_employee_details_by_id(employee_id: int, employee_details: schemas.EmployeeCreate, db: Session = Depends(get_db_session)):
    # Raises 404 if doesn't exist
    get_employee_by_id(employee_id, db)
    try:
        return crud_employees.update_employee(db, employee_id, employee_details)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")


# Delete an existing employee entry
@router.delete("/employee", response_model=schemas.Employee)
def delete_existing_employee_by_id(employee_id: int, db: Session = Depends(get_db_session)):
    # Raises 404 if doesn't exist
    get_employee_by_id(employee_id, db)
    return crud_employees.delete_employee(db, employee_id)


# Assign an employee to a practice
@router.put("/employee/practice", response_model=schemas.Employee)
def assign_employee_to_practice(employee_id: int, practice_id: int, db: Session = Depends(get_db_session)):
    return crud_employees.assign_employee_to_practice(db, employee_id, practice_id)


# Remove an employee from all practices
@router.delete("/employee/practice", response_model=schemas.Employee)
def unassign_employee_from_practice(employee_id: int, db: Session = Depends(get_db_session)):
    return crud_employees.unassign_employee_from_all_practices(db, employee_id)


@router.put("/employee/job_title", response_model=schemas.Employee)
def modify_job_title_for_employee(employee_id: int, job_title_id: int, db: Session = Depends(get_db_session)):
    return crud_employees.modify_job_title_for_employee_id(db, job_title_id, employee_id)


@router.get("/employees/practice", response_model=schemas.EmployeesForPractice)
def get_all_employees_for_practice(practice_id: int, db: Session = Depends(get_db_session)):
    try:
        employees = crud_employees.get_all_employees_for_practice_id(db, practice_id)
    except backend_api.exc.EmployeeNotFoundError:
        employees = []

    return {"practice_id": practice_id, "employees": employees}


@router.get("/employees/main_partners", response_model=List[schemas.Employee])
def get_main_partners_for_practice(practice_id: int, db: Session = Depends(get_db_session)):
    try:
        employees = crud_employees.get_main_partners_for_practice_id(db, practice_id)
    except backend_api.exc.EmployeeNotFoundError:
        employees = []
    return employees


@router.get("/job_titles", response_model=List[schemas.JobTitle])
def get_all_job_titles(db: Session = Depends(get_db_session)):
    return crud_employees.get_all_job_titles(db)


@router.get("/employees/count", response_model=schemas.RowCount)
def get_total_number_employees(db: Session = Depends(get_db_session)):
    return schemas.RowCount(count=crud_employees.read_total_number_of_employees(db))


@router.get("/employees/names", response_model=schemas.EntityNames)
def get_names_of_employees(db: Session = Depends(get_db_session)):
    return schemas.EntityNames(names=crud_employees.read_all_employee_names(db))
