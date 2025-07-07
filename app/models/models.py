from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import check_password_hash

@dataclass
class User(UserMixin):
    """User model with proper type hints and validation"""
    id: int
    username: str
    password_hash: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Convert string created_at to datetime if needed"""
        if isinstance(self.created_at, str):
            try:
                self.created_at = datetime.strptime(self.created_at, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                self.created_at = None
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self) -> str:
        """Return user ID as string (required by Flask-Login)"""
        return str(self.id)

@dataclass
class Movement:
    """Movement model with validation"""
    id: Optional[int]
    user_id: int
    fecha: str
    tipo: str
    categoria: str
    monto: float
    cuenta: str
    nota: str = ""
    descripcion: str = ""
    meta_asociada: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate movement data"""
        if self.tipo not in ['Ingreso', 'Gasto', 'Ahorro']:
            raise ValueError(f"Invalid movement type: {self.tipo}")
        
        if self.monto <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate date format
        try:
            datetime.strptime(self.fecha, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    @property
    def formatted_amount(self) -> str:
        """Return formatted amount with currency"""
        return f"${self.monto:,.2f}"
    
    @property
    def is_income(self) -> bool:
        """Check if movement is income"""
        return self.tipo == 'Ingreso'
    
    @property
    def is_expense(self) -> bool:
        """Check if movement is expense"""
        return self.tipo == 'Gasto'
    
    @property
    def is_saving(self) -> bool:
        """Check if movement is saving"""
        return self.tipo == 'Ahorro'

@dataclass
class Note:
    """Note model"""
    id: Optional[int]
    user_id: int
    fecha: str
    nota: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate note data"""
        if not self.nota.strip():
            raise ValueError("Note content cannot be empty")
        
        # Validate date format
        try:
            datetime.strptime(self.fecha, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

@dataclass
class FinancialSummary:
    """Financial summary model"""
    total_ingresos: float = 0.0
    total_gastos: float = 0.0
    total_ahorros: float = 0.0
    
    @property
    def saldo_neto(self) -> float:
        """Calculate net balance"""
        return self.total_ingresos - self.total_gastos - self.total_ahorros
    
    @property
    def formatted_ingresos(self) -> str:
        return f"${self.total_ingresos:,.2f}"
    
    @property
    def formatted_gastos(self) -> str:
        return f"${self.total_gastos:,.2f}"
    
    @property
    def formatted_ahorros(self) -> str:
        return f"${self.total_ahorros:,.2f}"
    
    @property
    def formatted_saldo_neto(self) -> str:
        return f"${self.saldo_neto:,.2f}"

@dataclass
class CategoryTotal:
    """Category total model"""
    categoria: str
    total: float
    
    @property
    def formatted_total(self) -> str:
        return f"${self.total:,.2f}"

@dataclass
class AccountBalance:
    """Account balance model"""
    cuenta: str
    saldo: float
    
    @property
    def formatted_saldo(self) -> str:
        return f"${self.saldo:,.2f}"
    
    @property
    def is_positive(self) -> bool:
        return self.saldo > 0