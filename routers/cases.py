from fastapi import APIRouter, Body, HTTPException, status
from models.case import Case

router = APIRouter()

@router.post("/",
             response_description="Case Created",
             response_model=Case,
             status_code=status.HTTP_201_CREATED
             )
async def create_case(case: Case = Body(...)):
    """Insert a new case. Make sure of the ID of the case"""
    fromCases = await Case.find_one(Case.case_id == case.case_id)
    if fromCases:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, detail = f"Case with id {case.case_id} already exists")
    await case.create()
    return case