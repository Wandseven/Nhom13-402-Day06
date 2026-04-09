from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, ClinicResponse
from app.services.booking_service import (
    create_appointment,
    get_appointment,
    list_appointments,
    get_clinics,
    get_clinic,
)

router = APIRouter(prefix="/api", tags=["Appointments & Clinics"])


# ── Appointments ──

@router.post("/appointments", response_model=AppointmentResponse)
async def create_new_appointment(data: AppointmentCreate, db: AsyncSession = Depends(get_db)):
    return await create_appointment(db, data)


@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_all_appointments(db: AsyncSession = Depends(get_db)):
    return await list_appointments(db)


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_single_appointment(appointment_id: str, db: AsyncSession = Depends(get_db)):
    appt = await get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch hẹn")
    return appt


# ── Clinics ──

@router.get("/clinics", response_model=list[ClinicResponse])
async def list_all_clinics(db: AsyncSession = Depends(get_db)):
    return await get_clinics(db)


@router.get("/clinics/{clinic_id}", response_model=ClinicResponse)
async def get_single_clinic(clinic_id: str, db: AsyncSession = Depends(get_db)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Không tìm thấy phòng khám")
    return clinic
