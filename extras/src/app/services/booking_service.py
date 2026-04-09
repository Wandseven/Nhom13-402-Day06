from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.appointment import Appointment
from app.models.clinic import Clinic
from app.schemas.appointment import AppointmentCreate


async def create_appointment(db: AsyncSession, data: AppointmentCreate) -> Appointment:
    appointment = Appointment(**data.model_dump())
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


async def get_appointment(db: AsyncSession, appointment_id: str) -> Appointment | None:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one_or_none()


async def list_appointments(db: AsyncSession, limit: int = 20) -> list[Appointment]:
    result = await db.execute(select(Appointment).order_by(Appointment.created_at.desc()).limit(limit))
    return list(result.scalars().all())


async def get_clinics(db: AsyncSession) -> list[Clinic]:
    result = await db.execute(select(Clinic))
    return list(result.scalars().all())


async def get_clinic(db: AsyncSession, clinic_id: str) -> Clinic | None:
    result = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
    return result.scalar_one_or_none()
