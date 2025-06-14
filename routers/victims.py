from fastapi import APIRouter, Body, HTTPException, status
from models.victim import Individual, UpdateVictimRisk

router = APIRouter()

@router.post("/",
    response_description = "Add a new victim or witness",
    response_model = Individual,
    status_code = status.HTTP_201_CREATED
)
async def add_victim(victim: Individual = Body(...)):
    """
    Add a new victim/witness.
    """

    if await Individual.find_one(Individual.individual_id == victim.individual_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An individual with the ID '{victim.individual_id}' already exists."
        )

    await victim.create()
    return victim

@router.get("/{victim_id}",
    response_description = "Get a single victim or witness by their ID",
    response_model = Individual
)
async def get_victim(victim_id: str):
    """
    Retrieve a single victim/witness by their human-readable individual_id.
    """

    if (victim := await Individual.find_one(Individual.individual_id == victim_id)) is not None:
        return victim

    raise HTTPException(status_code=404, detail=f"Individual with ID {victim_id} not found.")

@router.patch("/{victim_id}/risk",
    response_description = "Update the risk assessment for a victim or witness",
    response_model = Individual
)
async def update_victim_risk(victim_id: str, risk_data: UpdateVictimRisk):
    """
    Update the risk assessment fields for a specific individual.
    """
    # Create a dictionary of fields to update, using dot notation for nested objects
    update_dict = {
        f"risk_assessment.{key}": value
        for key, value in risk_data.model_dump(exclude_unset = True).items()
    }

    if len(update_dict) >= 1:
        updated_victim = await Individual.find_one(
            Individual.individual_id == victim_id
        ).update({"$set": update_dict})

        if updated_victim:
            if (victim := await Individual.find_one(Individual.individual_id == victim_id)) is not None:
                return victim

    if (existing_victim := await Individual.find_one(Individual.individual_id == victim_id)) is not None:
        return existing_victim

    raise HTTPException(status_code = 404, detail = f"Individual with ID {victim_id} not found")