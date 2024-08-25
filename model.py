from dataclasses import dataclass

@dataclass
class Customer:
    customer_id: int
    full_name: str
    age_years: int
    annual_income: float
    password_hash: str
    job_title: str
    education_level: str
    marital_status: str
    height_cm: float
    weight_kg: float
    waist_size_cm: float
    hip_size_cm: float
    systolic_bp: int
    diastolic_bp: int
    heart_rate: int
    cholesterol_level_mg: float
    glucose_level_mg: float
    hdl_level_mg: float
    ldl_level_mg: float
    triglycerides_level_mg: float
    uric_acid_level_mg: float
    chronic_illness_history: bool

@dataclass
class InsurancePlan:
    plan_id: int
    plan_name: str
    coverage_type: str
    base_cost: float

@dataclass
class InsuranceQuote:
    quote_id: int
    customer: Customer
    insurance_plan: InsurancePlan
    calculated_amount: float
    customer_income: float
    customer_age: int
    height_cm: float  # Height in cm
    weight_kg: float  # Weight in kg
    waist_size_cm: float  # Waist Circumference in cm
    hip_size_cm: float  # Hip Circumference in cm
    systolic_bp: int  # Systolic Blood Pressure
    diastolic_bp: int  # Diastolic Blood Pressure
    heart_rate_bpm: int  # Pulse in beats per minute
    cholesterol_level_mg: float  # Cholesterol level in mg/dL
    glucose_level_mg: float  # Blood Sugar level in mg/dL
    hdl_level_mg: float  # HDL level in mg/dL
    ldl_level_mg: float  # LDL level in mg/dL
    triglycerides_level_mg: float  # Triglycerides level in mg/dL
    uric_acid_level_mg: float  # Uric Acid level in mg/dL
    chronic_illness_history: bool  # Indicates Chronic Illness History
