from beanie import PydanticObjectId
from beanie.odm.operators.find.comparison import In
from fastapi import APIRouter, Body, HTTPException, status
from models.case import Case, UpdateCase, CaseStatusHistory
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.post("/",
    response_description = "Add new case",
    response_model = Case,
    status_code = status.HTTP_201_CREATED
)
async def create_case(case: Case = Body(...)):
    existing_case = await Case.find_one(Case.case_id == case.case_id)
    if existing_case:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"Case with ID {case.case_id} already exists."
        )
    await case.create()
    return case

@router.get("/{case_id}",
    response_description = "Get a single case by its ID",
    response_model = Case
)
async def get_case(case_id: str):
    """Get a single case by its ID"""
    case = await Case.find_one(Case.case_id == case_id)

    if not case:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Case with ID {case_id} not found."
        )
    return case

@router.get("/",
    response_description = "List all cases",
    response_model = List[Case]
)
async def list_cases(status: Optional[str] = None,
                     priority: Optional[str] = None,
                     violation_type: Optional[str] = None,
                     start_date: Optional[date] = None,
                     end_date: Optional[date] = None,
                     country: Optional[str] = None,
                     region: Optional[str] = None):
    """List all cases in the database with filtering"""
    search_filter = []
    search_filter.append(Case.is_archived == False)

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

    if country:
        search_filter.append(Case.location.country == country)

    if region:
        search_filter.append(Case.location.region == region)

    cases = await Case.find(*search_filter).to_list()
    return cases


@router.patch("/{id}",
              response_description = "Update a case and log status change",
              response_model = Case
)
async def update_case(id: PydanticObjectId, update_data: UpdateCase):
    """
    Update a case by its ID. If the status is changed, a log is created in the case_status_history collection.
    """
    case = await Case.get(id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID {id} is not found")

    previous_status = case.status

    update_dict = update_data.model_dump(exclude_unset=True)

    if len(update_dict) >= 1:
        await case.update({"$set": update_dict})

        new_status = update_dict.get("status")
        if new_status and new_status != previous_status:
            history_log = CaseStatusHistory(
                case_id = case.id,
                previous_status = previous_status,
                new_status = new_status,
                changed_by = case.created_by
            )
            await history_log.create()

    if (updated_case := await Case.get(id)) is not None:
        return updated_case

    raise HTTPException(status_code=404, detail=f"Case with ID {id} not found")

@router.delete("/{id}",
               response_description = "Archiving a case",
               status_code = status.HTTP_204_NO_CONTENT
)
async def archive_case(id: PydanticObjectId):
    """Archiving a case by ID"""
    case = await Case.get(id)

    if not case:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Case with ID {id} not found."
        )

    case.is_archived = True
    await case.save()

    return