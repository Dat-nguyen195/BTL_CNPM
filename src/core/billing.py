"""
billing.py – Ledger Management, Fee Calculations and Financial Invariants
Smart E-Mobility Hub – ĐHQG-HCM
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, time
import uuid
from core.policies import (
    SHARED_DEPOSIT_VND,
    SHARED_EXPIRY_MINUTES,
    SHARED_NOSHOW_PENALTY_VND,
    SHARED_NOSHOW_REFUND_VND,
    SHARED_FREE_MINUTES,
    SHARED_RATE_PER_MINUTE_VND,
    VOUCHER_DISCOUNT_VND,
    PARKING_PER_VISIT_VND,
    OVERSTAY_GRACE_MINUTES,
    OVERSTAY_FEE_PER_BLOCK_VND,
    get_kwh_rate,
    PEV_RESERVATION_DEPOSIT_VND,
    PEV_NOSHOW_PENALTY_VND,
    PEV_NOSHOW_REFUND_VND
)

def record_transaction(
    wallet: Dict[str, Any],
    tx_type: str,
    amount: int,
    booking_id: Optional[str] = None,
    note: str = "",
    sim_time: Optional[str] = None
) -> Dict[str, Any]:
    """Appends an immutable entry to the wallet ledger and validates balance."""
    if not sim_time:
        sim_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tx_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
    entry = {
        "tx_id": tx_id,
        "time": sim_time,
        "type": tx_type,
        "amount": amount,
        "balance_after": wallet.get("balance", 0),
        "held_after": wallet.get("held_deposit", 0),
        "debt_after": wallet.get("debt", 0),
        "booking_id": booking_id,
        "note": note
    }
    wallet.setdefault("ledger", []).append(entry)
    return entry

def hold_deposit(
    wallet: Dict[str, Any],
    amount: int = SHARED_DEPOSIT_VND,
    booking_id: Optional[str] = None,
    sim_time: Optional[str] = None
) -> Tuple[bool, str]:
    """Holds reservation deposit from available balance."""
    current_balance = wallet.get("balance", 0)
    debt = wallet.get("debt", 0)
    if debt > 0:
        return False, f"Tài khoản đang có khoản nợ chưa quyết toán ({debt:,} VNĐ). Vui lòng thanh toán nợ trước khi đặt xe mới."
    if current_balance < amount:
        return False, f"Số dư khả dụng ({current_balance:,} VNĐ) không đủ tiền đặt cọc ({amount:,} VNĐ)."
    
    wallet["balance"] = current_balance - amount
    new_held = wallet.get("held_deposit", 0) + amount
    wallet["held_deposit"] = new_held
    wallet["held"] = new_held
    record_transaction(
        wallet=wallet,
        tx_type="HOLD_DEPOSIT",
        amount=-amount,
        booking_id=booking_id,
        note=f"Tạm khóa tiền cọc giữ chỗ xe ({amount:,} VNĐ)",
        sim_time=sim_time
    )
    return True, "Khóa cọc giữ chỗ thành công."

def release_held_deposit_full(
    wallet: Dict[str, Any],
    amount: int = SHARED_DEPOSIT_VND,
    booking_id: Optional[str] = None,
    sim_time: Optional[str] = None
) -> bool:
    """Refunds 100% of held deposit back to balance (e.g. early cancellation within 30 min)."""
    held = wallet.get("held_deposit", wallet.get("held", 0))
    if held < amount:
        amount = held
    if amount <= 0:
        return False
    new_held = max(0, held - amount)
    wallet["held_deposit"] = new_held
    wallet["held"] = new_held
    wallet["balance"] = wallet.get("balance", 0) + amount
    record_transaction(
        wallet=wallet,
        tx_type="REFUND_DEPOSIT_FULL",
        amount=amount,
        booking_id=booking_id,
        note=f"Hoàn trả 100% tiền cọc do hủy đặt chỗ hợp lệ trong {SHARED_EXPIRY_MINUTES} phút ({amount:,} VNĐ)",
        sim_time=sim_time
    )
    return True

def settle_noshow_penalty(
    wallet: Dict[str, Any],
    booking_id: Optional[str] = None,
    sim_time: Optional[str] = None
) -> bool:
    """Settles held deposit upon expiry (no-show): 10,000 fee deducted, 40,000 refunded."""
    held = wallet.get("held_deposit", 0)
    if held < SHARED_DEPOSIT_VND:
        return False
    wallet["held_deposit"] = held - SHARED_DEPOSIT_VND
    wallet["balance"] = wallet.get("balance", 0) + SHARED_NOSHOW_REFUND_VND
    record_transaction(
        wallet=wallet,
        tx_type="PENALTY_NOSHOW",
        amount=-SHARED_NOSHOW_PENALTY_VND,
        booking_id=booking_id,
        note=f"Khấu trừ phí giữ chỗ quá {SHARED_EXPIRY_MINUTES} phút không nhận xe ({SHARED_NOSHOW_PENALTY_VND:,} VNĐ)",
        sim_time=sim_time
    )
    record_transaction(
        wallet=wallet,
        tx_type="REFUND_NOSHOW_REMAINDER",
        amount=SHARED_NOSHOW_REFUND_VND,
        booking_id=booking_id,
        note=f"Hoàn trả phần cọc còn lại sau phạt no-show ({SHARED_NOSHOW_REFUND_VND:,} VNĐ)",
        sim_time=sim_time
    )
    return True

def calculate_shared_rental_cost(
    duration_minutes: int,
    has_voucher: bool = False,
    extra_free_minutes: int = 0
) -> Dict[str, Any]:
    """Calculates shared EV rental fee according to approved policies."""
    total_free = SHARED_FREE_MINUTES + extra_free_minutes
    billable_minutes = max(0, duration_minutes - total_free)
    base_fee = billable_minutes * SHARED_RATE_PER_MINUTE_VND
    discount = min(base_fee, VOUCHER_DISCOUNT_VND) if has_voucher else 0
    final_fee = max(0, base_fee - discount)
    return {
        "duration_minutes": duration_minutes,
        "free_minutes": total_free,
        "billable_minutes": billable_minutes,
        "base_fee": base_fee,
        "discount": discount,
        "final_fee": final_fee
    }

def settle_shared_rental(
    wallet: Dict[str, Any],
    rental_cost: Dict[str, Any],
    booking_id: Optional[str] = None,
    sim_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Settles final trip fee against held deposit and wallet balance.
    If funds insufficient, records explicit debt instead of clamping to 0!
    """
    final_fee = rental_cost["final_fee"]
    held = wallet.get("held_deposit", 0)
    deposit_to_release = min(held, SHARED_DEPOSIT_VND)
    wallet["held_deposit"] = held - deposit_to_release
    refund_amount = 0
    deducted_from_available = 0
    
    # Net transaction from deposit
    if deposit_to_release >= final_fee:
        refund_amount = deposit_to_release - final_fee
        wallet["balance"] = wallet.get("balance", 0) + refund_amount
        record_transaction(
            wallet=wallet,
            tx_type="SETTLE_RENTAL_FEE",
            amount=-final_fee,
            booking_id=booking_id,
            note=f"Thanh toán phí thuê xe ({final_fee:,} VNĐ) từ tiền cọc; hoàn dư ({refund_amount:,} VNĐ)",
            sim_time=sim_time
        )
        debt_incurred = 0
    else:
        # Deposit was not enough
        shortfall = final_fee - deposit_to_release
        current_balance = wallet.get("balance", 0)
        deducted_from_available = min(current_balance, shortfall)
        if current_balance >= shortfall:
            wallet["balance"] = current_balance - shortfall
            debt_incurred = 0
            record_transaction(
                wallet=wallet,
                tx_type="SETTLE_RENTAL_FEE",
                amount=-final_fee,
                booking_id=booking_id,
                note=f"Thanh toán toàn bộ cọc ({deposit_to_release:,} VNĐ) + trích ví ({shortfall:,} VNĐ)",
                sim_time=sim_time
            )
        else:
            debt_incurred = shortfall - current_balance
            wallet["balance"] = 0
            wallet["debt"] = wallet.get("debt", 0) + debt_incurred
            record_transaction(
                wallet=wallet,
                tx_type="SETTLE_RENTAL_DEBT",
                amount=-(deposit_to_release + current_balance),
                booking_id=booking_id,
                note=f"Thanh toán một phần; ghi nợ minh bạch ({debt_incurred:,} VNĐ) vào tài khoản",
                sim_time=sim_time
            )

    invoice = {
        "invoice_id": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "booking_id": booking_id,
        "time": sim_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration_minutes": rental_cost["duration_minutes"],
        "free_minutes": rental_cost["free_minutes"],
        "billable_minutes": rental_cost["billable_minutes"],
        "base_fee": rental_cost["base_fee"],
        "discount": rental_cost["discount"],
        "total_fee": final_fee,
        "deposit_released": deposit_to_release,
        "refund_amount": refund_amount,
        "deducted_from_available": deducted_from_available,
        "debt_incurred": debt_incurred,
        "status": "PAID" if debt_incurred == 0 else "PARTIAL_DEBT"
    }
    return invoice

def calculate_private_ev_bill(
    parking_fee: int = PARKING_PER_VISIT_VND,
    kwh_consumed: float = 0.0,
    checkin_time_str: Optional[str] = None,
    overstay_minutes: int = 0
) -> Dict[str, Any]:
    """Calculates private EV parking + energy + overstay bill."""
    # Determine electricity tariff based on time
    t_obj = time(8, 0)
    if checkin_time_str:
        try:
            dt = datetime.strptime(checkin_time_str, "%Y-%m-%d %H:%M:%S")
            t_obj = dt.time()
        except ValueError:
            pass
    rate_per_kwh = get_kwh_rate(t_obj)
    energy_fee = int(round(kwh_consumed * rate_per_kwh))
    
    # Overstay calculation (blocks of 15 min after 15 min grace)
    overstay_fee = 0
    if overstay_minutes > OVERSTAY_GRACE_MINUTES:
        extra_minutes = overstay_minutes - OVERSTAY_GRACE_MINUTES
        blocks = (extra_minutes + 14) // 15
        overstay_fee = blocks * OVERSTAY_FEE_PER_BLOCK_VND
        
    total_bill = parking_fee + energy_fee + overstay_fee
    return {
        "parking_fee": parking_fee,
        "kwh_consumed": round(kwh_consumed, 2),
        "rate_per_kwh": rate_per_kwh,
        "energy_fee": energy_fee,
        "overstay_minutes": overstay_minutes,
        "overstay_fee": overstay_fee,
        "total_bill": total_bill
    }

def record_wallet_debt(
    wallet: Dict[str, Any],
    amount: int,
    reason: str = "",
    sim_time: Optional[str] = None
) -> None:
    """Explicitly records debt without silently clamping negative balances."""
    wallet["debt"] = wallet.get("debt", 0) + amount
    record_transaction(
        wallet=wallet,
        tx_type="RECORD_DEBT",
        amount=-amount,
        note=reason or f"Ghi nợ tài khoản ({amount:,} VNĐ)",
        sim_time=sim_time
    )

def settle_pev_noshow_penalty(
    wallet: Dict[str, Any],
    deposit_amount: int = PEV_RESERVATION_DEPOSIT_VND,
    penalty_amount: int = PEV_NOSHOW_PENALTY_VND,
    booking_id: Optional[str] = None,
    sim_time: Optional[str] = None
) -> bool:
    """Settles held PEV deposit upon expiry (no-show): penalty deducted, remainder refunded."""
    held = wallet.get("held_deposit", 0)
    actual_held_for_res = min(held, deposit_amount)
    if actual_held_for_res <= 0:
        return False
    refund_amount = max(0, actual_held_for_res - penalty_amount)
    actual_penalty = actual_held_for_res - refund_amount

    new_held = max(0, held - actual_held_for_res)
    wallet["held_deposit"] = new_held
    wallet["held"] = new_held
    wallet["balance"] = wallet.get("balance", 0) + refund_amount

    if actual_penalty > 0:
        record_transaction(
            wallet=wallet,
            tx_type="PENALTY_PEV_NOSHOW",
            amount=-actual_penalty,
            booking_id=booking_id,
            note=f"Khấu trừ phí giữ chỗ xe cá nhân quá hạn ({actual_penalty:,} VNĐ)",
            sim_time=sim_time
        )
    if refund_amount > 0:
        record_transaction(
            wallet=wallet,
            tx_type="REFUND_PEV_NOSHOW",
            amount=refund_amount,
            booking_id=booking_id,
            note=f"Hoàn trả tiền cọc giữ chỗ xe cá nhân sau phạt no-show ({refund_amount:,} VNĐ)",
            sim_time=sim_time
        )
    return True

def settle_overstay_charging(
    wallet: Dict[str, Any],
    session_id: str,
    vehicle_id: str,
    overstay_fee: int,
    energy_fee: int = 0,
    kwh_charged: float = 0.0,
    sim_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Settles overstay penalty and optional energy fee when unplugging vehicle from SS5.
    Deducts available balance or records explicit debt if balance is insufficient.
    Appends ledger transactions and returns complete invoice.
    """
    if not sim_time:
        sim_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_due = int(overstay_fee + energy_fee)
    current_bal = wallet.get("balance", 0)

    if total_due <= 0:
        return {
            "invoice_id": f"CINV-{uuid.uuid4().hex[:6].upper()}",
            "session_id": session_id,
            "vehicle_id": vehicle_id,
            "overstay_fee": 0,
            "energy_fee": 0,
            "kwh_charged": kwh_charged,
            "total_due": 0,
            "deducted": 0,
            "debt": 0,
            "time": sim_time,
            "status": "FREE"
        }

    if current_bal >= total_due:
        wallet["balance"] = current_bal - total_due
        deducted = total_due
        debt = 0
        record_transaction(
            wallet=wallet,
            tx_type="OVERSTAY_FEE" if overstay_fee > 0 else "CHARGING_FEE",
            amount=-total_due,
            booking_id=session_id,
            note=f"Thanh toán phí sạc/chiếm dụng cổng (Overstay) cho xe {vehicle_id} ({total_due:,} VNĐ)",
            sim_time=sim_time
        )
    else:
        deducted = current_bal
        wallet["balance"] = 0
        debt = total_due - deducted
        if deducted > 0:
            record_transaction(
                wallet=wallet,
                tx_type="OVERSTAY_PARTIAL",
                amount=-deducted,
                booking_id=session_id,
                note=f"Trích một phần số dư ví ({deducted:,} VNĐ) cho phí overstay xe {vehicle_id}",
                sim_time=sim_time
            )
        record_wallet_debt(
            wallet=wallet,
            amount=debt,
            reason=f"Ghi nợ phí chiếm dụng cổng sạc (Overstay) #{session_id} - xe {vehicle_id}",
            sim_time=sim_time
        )

    invoice = {
        "invoice_id": f"CINV-{uuid.uuid4().hex[:6].upper()}",
        "session_id": session_id,
        "vehicle_id": vehicle_id,
        "overstay_fee": overstay_fee,
        "energy_fee": energy_fee,
        "kwh_charged": kwh_charged,
        "total_due": total_due,
        "deducted": deducted,
        "debt": debt,
        "time": sim_time,
        "status": "PAID" if debt == 0 else "DEBT"
    }
    return invoice

