from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class RegisterRequest(BaseModel):
    mssv: str = Field(..., min_length=5, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=72)
    role: str = Field(default="STUDENT", pattern=r"^(STUDENT|OPERATOR)$")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateBookingRequest(BaseModel):
    hub_id: str
    vehicle_id: str
    destination_hub_id: Optional[str] = None
    voucher_code: Optional[str] = None

class PickupRequest(BaseModel):
    booking_id: str
    pin_code: str = Field(..., min_length=4, max_length=6)

class ReturnRequest(BaseModel):
    booking_id: str
    return_hub_id: str
    duration_minutes: int = Field(default=25, ge=1, le=600)

class RegisterPersonalEVRequest(BaseModel):
    plate: str = Field(..., min_length=5, max_length=20)
    type: str = Field(..., pattern=r"^(scooter|bike|car)$")
    brand: str = Field(..., min_length=2, max_length=80)
    battery_kwh: float = Field(..., gt=0.1, le=150.0)

class ReservePersonalSlotRequest(BaseModel):
    ev_id: str
    hub_id: str
    request_charging: bool = False
    current_soc: float = Field(default=50.0, ge=0, le=100)

class CheckoutPersonalRequest(BaseModel):
    reservation_id: str
    duration_hours: float = Field(default=2.0, gt=0, le=72)
    kwh_charged: float = Field(default=3.5, ge=0, le=150)
    overstay_minutes: int = Field(default=0, ge=0, le=300)

class DispatchCreateRequest(BaseModel):
    source_hub_id: str
    destination_hub_id: str
    vehicle_ids: List[str]
    reason: str