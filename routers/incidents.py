from fastapi import APIRouter, Form, File, UploadFile, HTTPException, status
from models.incident import IncidentReport, Evidence, UpdateIncidentReport, ViolationTypeAnalytics
from typing import List, Optional
from datetime import date, datetime
import json

import cloudinary
import cloudinary.uploader
from config import BaseConfig

settings = BaseConfig()
cloudinary.config(
    cloud_name = settings.CLOUDINARY_CLOUD_NAME,
    api_key = settings.CLOUDINARY_API_KEY,
    api_secret = settings.CLOUDINARY_SECRET_KEY,
)

router = APIRouter()

@router.post("/",
             response_description = "Submit a new incident report with evidence",
             response_model = IncidentReport,
             status_code = status.HTTP_201_CREATED
             )
async def create_incident_report(
        report_data: str = Form(...),
        evidence_file: Optional[UploadFile] = File(None)
):
    """
    Create a new incident report, accepting report details as a JSON string.
    """
    try:
        report = IncidentReport.model_validate_json(report_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code = 400, detail = "Invalid JSON format for report_data.")

    if await IncidentReport.find_one(IncidentReport.report_id == report.report_id):
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"Incident Report with ID {report.report_id} already exists."
        )

    if evidence_file:
        upload_result = cloudinary.uploader.upload(
            evidence_file.file,
            resource_type = "auto",
            folder = "incident_reports"
        )
        new_evidence = Evidence(
            type = upload_result.get("resource_type", "raw"),
            url = upload_result.get("secure_url"),
            description = evidence_file.filename
        )
        if report.evidence:
            report.evidence.append(new_evidence)
        else:
            report.evidence = [new_evidence]

    await report.create()
    return report


@router.get("/",
            response_description = "List all incident reports",
            response_model = List[IncidentReport]
            )
async def list_incident_reports(
        status: Optional[str] = None,
        country: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
):
    """
    Retrieve incident reports with optional filtering.
    """
    search_criteria = []
    if status:
        search_criteria.append(IncidentReport.status == status)

    if country:
        search_criteria.append(IncidentReport.incident_details.location.country == country)

    if start_date:
        search_criteria.append(IncidentReport.incident_details.date >= start_date)

    if end_date:
        search_criteria.append(IncidentReport.incident_details.date <= end_date)

    reports = await IncidentReport.find(*search_criteria).to_list()
    return reports


@router.patch("/{report_id}",
              response_description = "Update the status of an incident report",
              response_model = IncidentReport
              )
async def update_report_status(
        report_id: str,
        update_data: UpdateIncidentReport
):
    """
    Update the status of a report (e.g., from 'new' to 'verified').
    """
    update_dict = update_data.model_dump(exclude_unset=True)

    if len(update_dict) >= 1:
        updated_report = await IncidentReport.find_one(
            IncidentReport.report_id == report_id
        ).update({"$set": update_dict})

        if updated_report:
            if (report := await IncidentReport.find_one(IncidentReport.report_id == report_id)) is not None:
                return report

    if (existing_report := await IncidentReport.find_one(IncidentReport.report_id == report_id)) is not None:
        return existing_report

    raise HTTPException(status_code = 404, detail = f"Incident Report {report_id} not found")


@router.get("/analytics/violations",
            response_description = "Get a count of reports by violation type",
            response_model = List[ViolationTypeAnalytics]
            )
async def get_reports_by_violation_type():
    """
    Performs an aggregation to count incident reports grouped by violation type.
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