from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List

class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mssv: str = Field(..., min_length=5, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_size(cls, password: str) -> str:
        if len(password.encode()) > 72:
            raise ValueError("Mật khẩu không được dài quá 72 byte UTF-8.")
        return password

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

class RerouteBookingRequest(BaseModel):
    booking_id: str
    new_destination_hub_id: str

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

class IncidentIsolateRequest(BaseModel):
    hub_id: str
    target_type: str = Field(..., pattern=r"^(VEHICLE|PORT)$")
    vehicle_id: Optional[str] = None

class SimMetroSurgeRequest(BaseModel):
    target_hub_id: str = "HUB-002"
    num_new_students: int = Field(default=20, ge=1, le=100)
    seed: int = 42

class SimPortFailureRequest(BaseModel):
    target_hub_id: str = "HUB-004"
    num_ports_down: int = Field(default=3, ge=1, le=20)
    seed: int = 42