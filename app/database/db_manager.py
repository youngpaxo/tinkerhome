import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations with proper connection management"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Movimientos table with better constraints
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN ('Ingreso', 'Gasto', 'Ahorro')),
                    categoria TEXT NOT NULL,
                    monto REAL NOT NULL CHECK (monto > 0),
                    cuenta TEXT NOT NULL,
                    nota TEXT DEFAULT '',
                    descripcion TEXT DEFAULT '',
                    meta_asociada TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            
            # Notas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    nota TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_movimientos_user_id ON movimientos(user_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_movimientos_tipo ON movimientos(tipo);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_user_id ON notas(user_id);")
            
            conn.commit()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_single_query(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Execute a SELECT query and return single result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """Execute an INSERT query and return the last row id"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """Execute an UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    # User operations
    def create_user(self, username: str, password_hash: str) -> int:
        """Create a new user"""
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.execute_insert(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, created_at)
        )
    
    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """Get user by ID"""
        return self.execute_single_query(
            "SELECT id, username, password_hash, created_at FROM users WHERE id = ?",
            (user_id,)
        )
    
    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        """Get user by username"""
        return self.execute_single_query(
            "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
            (username,)
        )
    
    # Movement operations
    def create_movement(self, user_id: int, fecha: str, tipo: str, categoria: str, 
                       monto: float, cuenta: str, nota: str = "", 
                       descripcion: str = "", meta_asociada: str = "") -> int:
        """Create a new movement"""
        return self.execute_insert("""
            INSERT INTO movimientos (
                user_id, fecha, tipo, categoria, monto,
                cuenta, nota, descripcion, meta_asociada
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, fecha, tipo, categoria, monto, cuenta, nota, descripcion, meta_asociada))
    
    def get_recent_movements(self, user_id: int, tipo: str = None, limit: int = 5) -> List[sqlite3.Row]:
        """Get recent movements for a user"""
        if tipo:
            return self.execute_query("""
                SELECT fecha, monto, nota, categoria, cuenta
                FROM movimientos
                WHERE user_id = ? AND tipo = ?
                ORDER BY fecha DESC, created_at DESC
                LIMIT ?
            """, (user_id, tipo, limit))
        else:
            return self.execute_query("""
                SELECT fecha, monto, nota, categoria, cuenta, tipo
                FROM movimientos
                WHERE user_id = ?
                ORDER BY fecha DESC, created_at DESC
                LIMIT ?
            """, (user_id, limit))
    
    def get_movements_by_filter(self, user_id: int, tipo: str = None) -> List[sqlite3.Row]:
        """Get movements with optional type filter"""
        if tipo:
            return self.execute_query("""
                SELECT * FROM movimientos
                WHERE user_id = ? AND tipo = ?
                ORDER BY fecha DESC, created_at DESC
            """, (user_id, tipo))
        else:
            return self.execute_query("""
                SELECT * FROM movimientos
                WHERE user_id = ?
                ORDER BY fecha DESC, created_at DESC
            """, (user_id,))
    
    def delete_movement(self, movement_id: int, user_id: int) -> bool:
        """Delete a movement (only if it belongs to the user)"""
        affected_rows = self.execute_update(
            "DELETE FROM movimientos WHERE id = ? AND user_id = ?",
            (movement_id, user_id)
        )
        return affected_rows > 0
    
    def get_totals_by_type(self, user_id: int) -> List[sqlite3.Row]:
        """Get totals grouped by movement type"""
        return self.execute_query("""
            SELECT tipo, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ?
            GROUP BY tipo
        """, (user_id,))
    
    def get_totals_by_category(self, user_id: int, tipo: str = None) -> List[sqlite3.Row]:
        """Get totals grouped by category"""
        if tipo:
            return self.execute_query("""
                SELECT categoria, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ? AND tipo = ?
                GROUP BY categoria
                ORDER BY total DESC
            """, (user_id, tipo))
        else:
            return self.execute_query("""
                SELECT categoria, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ?
                GROUP BY categoria
                ORDER BY total DESC
            """, (user_id,))
    
    def get_daily_totals(self, user_id: int, tipo: str = None) -> List[sqlite3.Row]:
        """Get totals grouped by date"""
        if tipo:
            return self.execute_query("""
                SELECT fecha, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ? AND tipo = ?
                GROUP BY fecha
                ORDER BY fecha ASC
            """, (user_id, tipo))
        else:
            return self.execute_query("""
                SELECT fecha, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ?
                GROUP BY fecha
                ORDER BY fecha ASC
            """, (user_id,))
    
    def get_monthly_totals(self, user_id: int, tipo: str = None) -> List[sqlite3.Row]:
        """Get totals grouped by month"""
        if tipo:
            return self.execute_query("""
                SELECT substr(fecha, 1, 7) as mes, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ? AND tipo = ?
                GROUP BY mes
                ORDER BY mes ASC
            """, (user_id, tipo))
        else:
            return self.execute_query("""
                SELECT substr(fecha, 1, 7) as mes, SUM(monto) as total
                FROM movimientos
                WHERE user_id = ?
                GROUP BY mes
                ORDER BY mes ASC
            """, (user_id,))
    
    def get_accounts(self, user_id: int) -> List[str]:
        """Get list of unique accounts for a user"""
        rows = self.execute_query("""
            SELECT DISTINCT cuenta
            FROM movimientos
            WHERE user_id = ?
            ORDER BY cuenta
        """, (user_id,))
        return [row["cuenta"] for row in rows]
    
    def get_account_balances(self, user_id: int) -> List[sqlite3.Row]:
        """Get balance by account"""
        return self.execute_query("""
            SELECT cuenta,
                   SUM(CASE WHEN tipo='Ingreso' THEN monto ELSE 0 END) -
                   SUM(CASE WHEN tipo='Gasto' THEN monto ELSE 0 END) -
                   SUM(CASE WHEN tipo='Ahorro' THEN monto ELSE 0 END) as saldo
            FROM movimientos
            WHERE user_id = ?
            GROUP BY cuenta
            ORDER BY saldo DESC
        """, (user_id,))
    
    def get_goals(self, user_id: int) -> List[str]:
        """Get list of unique goals for a user"""
        rows = self.execute_query("""
            SELECT DISTINCT meta_asociada
            FROM movimientos
            WHERE user_id = ? AND meta_asociada != ''
            ORDER BY meta_asociada
        """, (user_id,))
        return [row["meta_asociada"] for row in rows]
    
    def get_top_expense_categories(self, user_id: int, limit: int = 5) -> List[sqlite3.Row]:
        """Get top expense categories"""
        return self.execute_query("""
            SELECT categoria, SUM(monto) as total
            FROM movimientos
            WHERE user_id = ? AND tipo = 'Gasto'
            GROUP BY categoria
            ORDER BY total DESC
            LIMIT ?
        """, (user_id, limit))
    
    # Notes operations
    def create_note(self, user_id: int, fecha: str, nota: str) -> int:
        """Create a new note"""
        return self.execute_insert(
            "INSERT INTO notas (user_id, fecha, nota) VALUES (?, ?, ?)",
            (user_id, fecha, nota)
        )
    
    def get_notes(self, user_id: int) -> List[sqlite3.Row]:
        """Get all notes for a user"""
        return self.execute_query("""
            SELECT id, fecha, nota, created_at
            FROM notas
            WHERE user_id = ?
            ORDER BY fecha DESC, created_at DESC
        """, (user_id,))