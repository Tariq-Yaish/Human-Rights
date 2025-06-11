from fastapi import APIRouter, Body, HTTPException, status
from beanie import PydanticObjectId
from models.case import Case

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
async def get_case(case_id: PydanticObjectId):
    case = await Case.get(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found."
        )
    return case