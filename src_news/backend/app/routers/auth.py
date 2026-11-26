import uuid
from fastapi import APIRouter, HTTPException, status, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas import RegisterRequest, LoginRequest
from app.database import supabase
from app.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest):
    # Kiểm tra trùng email hoặc MSSV
    email = body.email.lower()
    student_id = body.mssv.strip().upper()
    same_email = supabase.table("users").select("user_id").eq("email", email).limit(1).execute()
    same_student = supabase.table("users").select("user_id").eq("mssv", student_id).limit(1).execute()
    if same_email.data or same_student.data:
        raise HTTPException(status_code=400, detail="Email hoặc MSSV đã được đăng ký.")

    hashed_pw = get_password_hash(body.password)
    user_res = supabase.table("users").insert({
        "mssv": student_id,
        "email": email,
        "full_name": body.full_name.strip(),
        "password_hash": hashed_pw,
        "role": "STUDENT"
    }).execute()

    new_user = user_res.data[0]
    user_id = new_user["user_id"]

    # Khởi tạo ví điện tử 150,000đ cho tài khoản mới
    supabase.table("wallets").insert({
        "user_id": user_id,
        "balance": 150000,
        "held_deposit": 0,
        "debt": 0
    }).execute()

    supabase.table("ledger_transactions").insert({
        "tx_id": f"TX-{uuid.uuid4().hex[:8].upper()}",
        "user_id": user_id,
        "tx_type": "DEPOSIT_TOPUP",
        "amount": 150000,
        "balance_after": 150000,
        "held_after": 0,
        "debt_after": 0,
        "note": "Nạp tiền khởi tạo tài khoản ĐHQG-HCM"
    }).execute()

    token = create_access_token({"sub": user_id, "role": new_user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "mssv": new_user["mssv"],
            "email": new_user["email"],
            "full_name": new_user["full_name"],
            "role": new_user["role"]
        }
    }

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    res = supabase.table("users").select("*").eq("email", body.email.lower()).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")

    user = res.data[0]
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")

    token = create_access_token({"sub": user["user_id"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "mssv": user["mssv"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    wallet_res = supabase.table("wallets").select("*").eq("user_id", current_user["user_id"]).execute()
    tx_res = supabase.table("ledger_transactions").select("*").eq("user_id", current_user["user_id"]).order("created_at", desc=True).limit(20).execute()
    return {
        "user": current_user,
        "wallet": wallet_res.data[0] if wallet_res.data else None,
        "ledger": tx_res.data
    }