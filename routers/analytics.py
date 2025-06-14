from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from models.case import Case
from models.incident import IncidentReport, ViolationTypeAnalytics

router = APIRouter()

@router.get("/violations",
            response_description = "Get a count of reports by violation type",
            response_model = List[ViolationTypeAnalytics]
            )
async def get_reports_by_violation_type():
    """
    Performs an aggregation to count incident reports grouped by violation type.
    This provides insights into the most common types of human rights violations.
    """
    pipeline = [
        {"$unwind": "$incident_details.violation_types"},
        {"$group": {
            "_id": "$incident_details.violation_types",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]

    analytics_result = await IncidentReport.aggregate(pipeline).to_list()
    return analytics_result

@router.get("/geodata",
            response_description="Get geographical distribution of incident reports",
            response_model=List[Dict[str, Any]]
)
async def get_incident_geodata(country: Optional[str] = None, region: Optional[str] = None):
    """
    Retrieves aggregated geographical data for incident reports,
    showing counts per country/region, suitable for map visualizations.
    Filters can be applied by country and region.
    """
    pipeline = []

    match_criteria = {}
    if country:
        match_criteria["incident_details.location.country"] = country
    if region:
        match_criteria["incident_details.location.region"] = region

    if match_criteria:
        pipeline.append({"$match": match_criteria})

    pipeline.append({
        "$group": {
            "_id": {
                "country": "$incident_details.location.country",
                "region": "$incident_details.location.region",
                "coordinates": "$incident_details.location.coordinates" # Include coordinates if available
            },
            "count": {"$sum": 1}
        }
    })

    pipeline.append({
        "$project": {
            "country": "$_id.country",
            "region": "$_id.region",
            "coordinates": "$_id.coordinates",
            "count": 1,
            "_id": 0 # Exclude default _id
        }
    })

    pipeline.append({"$sort": {"count": -1, "country": 1, "region": 1}})

    geodata_result = await IncidentReport.aggregate(pipeline).to_list()
    return geodata_result


@router.get("/timeline",
            response_description="Get incident reports trend over time",
            response_model=List[Dict[str, Any]]
            )
async def get_incident_timeline(
        granularity: str = "month",  # 'year', 'month', 'day'
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
):
    """
    Retrieves the number of incident reports over time,
    with configurable granularity (year, month, or day) and date range filtering.
    This helps identify trends and periods of increased activity.
    """
    if granularity not in ["year", "month", "day"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid granularity. Must be 'year', 'month', or 'day'."
        )

    pipeline = []

    date_match_criteria = {}
    if start_date:
        date_match_criteria["$gte"] = datetime.combine(start_date, datetime.min.time())
    if end_date:
        date_match_criteria["$lte"] = datetime.combine(end_date, datetime.max.time())

    if date_match_criteria:
        pipeline.append({"$match": {"incident_details.date": date_match_criteria}})

    group_id = {}
    if granularity == "year":
        group_id["year"] = {"$year": "$incident_details.date"}
    elif granularity == "month":
        group_id["year"] = {"$year": "$incident_details.date"}
        group_id["month"] = {"$month": "$incident_details.date"}
    elif granularity == "day":
        group_id["year"] = {"$year": "$incident_details.date"}
        group_id["month"] = {"$month": "$incident_details.date"}
        group_id["day"] = {"$dayOfMonth": "$incident_details.date"}

    pipeline.append({
        "$group": {
            "_id": group_id,
            "count": {"$sum": 1}
        }
    })

    sort_stage = {"_id.year": 1}
    if granularity == "month":
        sort_stage["_id.month"] = 1
    elif granularity == "day":
        sort_stage["_id.month"] = 1
        sort_stage["_id.day"] = 1

    pipeline.append({"$sort": sort_stage})
    pipeline.append({
        "$project": {
            "period": {
                "$concat": [
                    {"$toString": "$_id.year"},
                    {"$cond": {"if": {"$ne": ["$_id.month", None]}, "then": {"$concat": ["-", {"$toString": "$_id.month"}]}, "else": ""}},
                    {"$cond": {"if": {"$ne": ["$_id.day", None]}, "then": {"$concat": ["-", {"$toString": "$_id.day"}]}, "else": ""}}
                ]
            },
            "count": 1,
            "_id": 0
        }
    })

    timeline_result = await IncidentReport.aggregate(pipeline).to_list()
    return timeline_result
