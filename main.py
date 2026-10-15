from fastapi import FastAPI
from pydantic import BaseModel
import math

# Khởi tạo ứng dụng FastAPI
app = FastAPI(title="TechOne Smart SCM API - Backend Lõi")

# ==========================================
# 1. Định nghĩa Models (Cấu trúc dữ liệu đầu vào)
# ==========================================

class InventoryParams(BaseModel):
    annual_demand: int = 18000          # Nhu cầu năm (D)
    order_cost: float = 600000.0        # Chi phí đặt hàng (S)
    holding_cost: float = 15000.0       # Chi phí lưu kho (H)
    lead_time: float = 8.0              # Thời gian giao hàng (L)
    working_days: int = 300             # Số ngày làm việc
    safety_stock: int = 200             # Tồn kho an toàn (SS)

class SimulationParams(BaseModel):
    alpha_defect_rate: float            # Tỷ lệ lỗi thực tế của Alpha (%)
    alpha_lead_time: float              # Thời gian giao hàng hiện tại của Alpha
    alpha_price: float = 250000.0       # Đơn giá Alpha
    beta_price: float = 260000.0        # Đơn giá Beta (Dự phòng)
    order_volume: int = 1200            # Khối lượng đặt hàng giả định (1 lô EOQ)

# ==========================================
# 2. Các Endpoints (API Xử lý thuật toán)
# ==========================================

@app.post("/api/inventory/dynamic-rop")
def calculate_dynamic_inventory(params: InventoryParams):
    """
    API 1: Module Smart SCM & Dynamic Inventory
    Tính toán Lượng đặt hàng kinh tế (EOQ) và Điểm đặt hàng lại động (Dynamic ROP)
    """
    # 1. Thuật toán EOQ: Căn bậc 2 của (2 * D * S / H)
    eoq = math.sqrt((2 * params.annual_demand * params.order_cost) / params.holding_cost)
    
    # 2. Nhu cầu trung bình ngày (d)
    daily_demand = params.annual_demand / params.working_days
    
    # 3. Thuật toán Dynamic ROP: Tính lại điểm ROP nếu Lead time thay đổi
    dynamic_rop = (daily_demand * params.lead_time) + params.safety_stock
    
    return {
        "status": "success",
        "data": {
            "eoq_optimal_qty": math.ceil(eoq),
            "daily_demand": round(daily_demand, 2),
            "dynamic_rop": math.ceil(dynamic_rop),
            "warning": "CẢNH BÁO: ROP đã dâng cao do Lead time tăng!" if params.lead_time > 8 else "Bình thường"
        }
    }

@app.post("/api/simulation/dual-sourcing")
def simulate_dual_sourcing(params: SimulationParams):
    """
    API 2: Module Risk Simulation & Dual Sourcing Dashboard
    Thuật toán AI tự động điều hướng đơn hàng dựa trên tỷ lệ lỗi (AQL)
    """
    aql_threshold = 1.0  # Ngưỡng chấp nhận AQL là 1.0%
    
    # Kịch bản bình thường: 80% Alpha - 20% Beta
    allocation_alpha = 80
    allocation_beta = 20
    system_status = "NORMAL"
    ai_action = "Hệ thống hoạt động ổn định. Duy trì tỷ lệ Dual Sourcing 80/20."
    
    # Kích hoạt sự cố (Trigger) khi tỷ lệ lỗi vượt ngưỡng AQL
    if params.alpha_defect_rate > aql_threshold:
        allocation_alpha = 0
        allocation_beta = 100
        system_status = "CRITICAL_RISK"
        ai_action = "Kích hoạt Dual Sourcing: Tạm ngưng Alpha, tự động đẩy 100% sản lượng sang cho Beta để lấp đầy kho và cứu chuyền SMT."
    
    # Phân tích tác động tài chính (Delta Cost)
    base_cost = (0.8 * params.alpha_price + 0.2 * params.beta_price) * params.order_volume
    new_cost = (allocation_alpha / 100 * params.alpha_price + allocation_beta / 100 * params.beta_price) * params.order_volume
    delta_cost = new_cost - base_cost
    
    return {
        "status": system_status,
        "ai_recommendation": ai_action,
        "dual_sourcing_allocation": {
            "alpha_percent": allocation_alpha,
            "beta_percent": allocation_beta
        },
        "financial_impact": {
            "original_cost_vnd": base_cost,
            "new_cost_vnd": new_cost,
            "delta_cost_vnd": delta_cost,
            "message": f"Chi phí mua hàng chênh lệch {delta_cost:,.0f} VNĐ do chuyển dịch nhà cung cấp."
        }
    }

# Lệnh để chạy server test nội bộ:
# uvicorn main:app --reload