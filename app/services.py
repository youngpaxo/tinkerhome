from typing import List, Optional, Dict, Any
from app.database.db_manager import DatabaseManager
from app.models.models import User, Movement, Note, FinancialSummary, CategoryTotal, AccountBalance
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

class FinanceService:
    """Service layer for financial operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def calculate_financial_summary(self, user_id: int) -> FinancialSummary:
        """Calculate financial summary for a user"""
        try:
            totals = self.db.get_totals_by_type(user_id)
            
            summary = FinancialSummary()
            for row in totals:
                if row["tipo"] == "Ingreso":
                    summary.total_ingresos = float(row["total"] or 0)
                elif row["tipo"] == "Gasto":
                    summary.total_gastos = float(row["total"] or 0)
                elif row["tipo"] == "Ahorro":
                    summary.total_ahorros = float(row["total"] or 0)
            
            return summary
        except Exception as e:
            logger.error(f"Error calculating financial summary for user {user_id}: {e}")
            return FinancialSummary()
    
    def get_recent_movements(self, user_id: int, movement_type: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent movements for a user"""
        try:
            rows = self.db.get_recent_movements(user_id, movement_type, limit)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting recent movements for user {user_id}: {e}")
            return []
    
    def create_movement(self, user_id: int, movement_data: Dict[str, Any]) -> bool:
        """Create a new movement with validation"""
        try:
            # Create movement object for validation
            movement = Movement(
                id=None,
                user_id=user_id,
                fecha=movement_data['fecha'],
                tipo=movement_data['tipo'],
                categoria=movement_data['categoria'],
                monto=float(movement_data['monto']),
                cuenta=movement_data['cuenta'],
                nota=movement_data.get('nota', ''),
                descripcion=movement_data.get('descripcion', ''),
                meta_asociada=movement_data.get('meta_asociada', '')
            )
            
            # Save to database
            movement_id = self.db.create_movement(
                user_id=movement.user_id,
                fecha=movement.fecha,
                tipo=movement.tipo,
                categoria=movement.categoria,
                monto=movement.monto,
                cuenta=movement.cuenta,
                nota=movement.nota,
                descripcion=movement.descripcion,
                meta_asociada=movement.meta_asociada
            )
            
            logger.info(f"Created movement {movement_id} for user {user_id}")
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Validation error creating movement for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating movement for user {user_id}: {e}")
            return False
    
    def delete_movement(self, movement_id: int, user_id: int) -> bool:
        """Delete a movement"""
        try:
            success = self.db.delete_movement(movement_id, user_id)
            if success:
                logger.info(f"Deleted movement {movement_id} for user {user_id}")
            else:
                logger.warning(f"Failed to delete movement {movement_id} for user {user_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting movement {movement_id} for user {user_id}: {e}")
            return False
    
    def get_movements_with_filter(self, user_id: int, movement_type: str = None) -> List[Dict[str, Any]]:
        """Get movements with optional type filter"""
        try:
            rows = self.db.get_movements_by_filter(user_id, movement_type)
            movements = []
            for row in rows:
                movement_dict = dict(row)
                movement_dict['monto'] = float(movement_dict['monto'])
                movements.append(movement_dict)
            return movements
        except Exception as e:
            logger.error(f"Error getting movements for user {user_id}: {e}")
            return []
    
    def get_category_totals(self, user_id: int, movement_type: str = None) -> List[CategoryTotal]:
        """Get totals by category"""
        try:
            rows = self.db.get_totals_by_category(user_id, movement_type)
            return [CategoryTotal(categoria=row["categoria"], total=float(row["total"])) for row in rows]
        except Exception as e:
            logger.error(f"Error getting category totals for user {user_id}: {e}")
            return []
    
    def get_account_balances(self, user_id: int) -> List[AccountBalance]:
        """Get account balances"""
        try:
            rows = self.db.get_account_balances(user_id)
            return [AccountBalance(cuenta=row["cuenta"], saldo=float(row["saldo"])) for row in rows]
        except Exception as e:
            logger.error(f"Error getting account balances for user {user_id}: {e}")
            return []
    
    def get_accounts(self, user_id: int) -> List[str]:
        """Get list of accounts"""
        try:
            return self.db.get_accounts(user_id)
        except Exception as e:
            logger.error(f"Error getting accounts for user {user_id}: {e}")
            return []
    
    def get_goals(self, user_id: int) -> List[str]:
        """Get list of goals"""
        try:
            return self.db.get_goals(user_id)
        except Exception as e:
            logger.error(f"Error getting goals for user {user_id}: {e}")
            return []
    
    def get_top_expense_categories(self, user_id: int, limit: int = 5) -> List[CategoryTotal]:
        """Get top expense categories"""
        try:
            rows = self.db.get_top_expense_categories(user_id, limit)
            return [CategoryTotal(categoria=row["categoria"], total=float(row["total"])) for row in rows]
        except Exception as e:
            logger.error(f"Error getting top expense categories for user {user_id}: {e}")
            return []

class UserService:
    """Service layer for user operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_user(self, username: str, password: str) -> Optional[int]:
        """Create a new user with validation"""
        try:
            # Basic validation
            if not username or not username.strip():
                raise ValueError("Username cannot be empty")
            
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")
            
            # Check if user already exists
            existing_user = self.db.get_user_by_username(username.strip())
            if existing_user:
                raise ValueError("Username already exists")
            
            # Create user
            password_hash = generate_password_hash(password)
            user_id = self.db.create_user(username.strip(), password_hash)
            
            logger.info(f"Created user {username} with ID {user_id}")
            return user_id
            
        except ValueError as e:
            logger.warning(f"Validation error creating user {username}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user and return User object"""
        try:
            if not username or not password:
                return None
            
            row = self.db.get_user_by_username(username.strip())
            if not row:
                return None
            
            user = User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                created_at=row["created_at"]
            )
            
            if user.check_password(password):
                logger.info(f"User {username} authenticated successfully")
                return user
            
            logger.warning(f"Failed authentication attempt for user {username}")
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            row = self.db.get_user_by_id(user_id)
            if not row:
                return None
            
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                created_at=row["created_at"]
            )
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

class NotesService:
    """Service layer for notes operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_note(self, user_id: int, fecha: str, nota_texto: str) -> bool:
        """Create a new note with validation"""
        try:
            # Create note object for validation
            note = Note(
                id=None,
                user_id=user_id,
                fecha=fecha,
                nota=nota_texto
            )
            
            # Save to database
            note_id = self.db.create_note(user_id, fecha, nota_texto)
            logger.info(f"Created note {note_id} for user {user_id}")
            return True
            
        except ValueError as e:
            logger.error(f"Validation error creating note for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating note for user {user_id}: {e}")
            return False
    
    def get_notes(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all notes for a user"""
        try:
            rows = self.db.get_notes(user_id)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting notes for user {user_id}: {e}")
            return []