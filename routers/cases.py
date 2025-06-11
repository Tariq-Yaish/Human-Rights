from beanie.odm.operators.find.comparison import In
from fastapi import APIRouter, Body, HTTPException, status
from models.case import Case
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.post("/",
    response_description="Add new case",
    response_model=Case,
    status_code=status.HTTP_201_CREATED
)
async def create_case(case: Case = Body(...)):
    existing_case = await Case.find_one(Case.case_id == case.case_id)
    if existing_case:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case with ID {case.case_id} already exists."
        )
    await case.create()
    return case

@router.get("/{case_id}",
    response_description="Get a single case by its ID",
    response_model=Case
)
async def get_case(case_id: str):
    """Get a single case by its ID"""
    case = await Case.find_one(Case.case_id == case_id)

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found."
        )
    return case

@router.get("/",
    response_description="List all cases",
    response_model=List[Case]
)
async def list_cases(status: Optional[str] = None,
                     priority: Optional[str] = None,
                     violation_type: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None):
    """List all cases in the database with filtering"""
    search_filter = []
    if status:
        search_filter.append(Case.status == status)

    if priority:
        search_filter.append(Case.priority == priority)

    if violation_type:
        search_filter.append(In(Case.violation_types, [violation_type]))

    if start_date:
        search_filter.append(Case.date_occurred >= start_date)

    if end_date:
        search_filter.append(Case.date_occurred <= end_date)

    cases = await Case.find(*search_filter).to_list()
    return cases