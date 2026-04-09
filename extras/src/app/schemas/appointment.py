from pydantic import BaseModel


class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: str
    symptoms: str = ""
    clinic_id: str
    clinic_name: str
    appointment_date: str
    appointment_time: str
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: str
    patient_name: str
    patient_phone: str
    symptoms: str
    clinic_id: str
    clinic_name: str
    appointment_date: str
    appointment_time: str
    status: str
    notes: str | None = None

    model_config = {"from_attributes": True}


class ClinicResponse(BaseModel):
    id: str
    name: str
    address: str
    city: str
    district: str
    phone: str
    specialties: str
    latitude: float
    longitude: float
    opening_hours: str

    model_config = {"from_attributes": True}
