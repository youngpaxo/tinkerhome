from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services import FinanceService, NotesService
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

def init_main_routes(finance_service: FinanceService, notes_service: NotesService):
    """
    Initialize all main application routes with dependency injection
    """

    # -------------------------------
    # Dashboard
    # -------------------------------
    @main_bp.route("/")
    @login_required
    def index():
        try:
            summary = finance_service.calculate_financial_summary(current_user.id)
            recent_ingresos = finance_service.get_recent_movements(
                current_user.id, "Ingreso", limit=5
            )
            recent_gastos = finance_service.get_recent_movements(
                current_user.id, "Gasto", limit=5
            )
            return render_template(
                "index.html",
                ultimos_ingresos=recent_ingresos,
                ultimos_gastos=recent_gastos,
                total_ingresos=summary.total_ingresos,
                total_gastos=summary.total_gastos,
                total_ahorros=summary.total_ahorros,
                saldo_neto=summary.saldo_neto
            )
        except Exception as e:
            logger.error(f"Error loading dashboard for user {current_user.id}: {e}")
            flash("Error loading dashboard", "error")
            return render_template("index.html")

    # -------------------------------
    # Movimientos
    # -------------------------------
    @main_bp.route("/movimientos", methods=["GET", "POST"])
    @login_required
    def movimientos():
        if request.method == "POST":
            try:
                movement_data = {
                    'fecha': request.form.get("fecha"),
                    'tipo': request.form.get("tipo"),
                    'categoria': request.form.get("categoria"),
                    'monto': request.form.get("monto"),
                    'cuenta': request.form.get("cuenta"),
                    'nota': request.form.get("nota", ""),
                    'descripcion': request.form.get("descripcion", ""),
                    'meta_asociada': request.form.get("meta_asociada", "")
                }
                required_fields = ['fecha', 'tipo', 'categoria', 'monto', 'cuenta']
                missing_fields = [field for field in required_fields if not movement_data.get(field)]
                if missing_fields:
                    flash(f"Missing required fields: {', '.join(missing_fields)}", "error")
                else:
                    success = finance_service.create_movement(current_user.id, movement_data)
                    if success:
                        flash("Movement created successfully", "success")
                        return redirect(url_for("main.movimientos"))
                    else:
                        flash("Error creating movement", "error")
            except Exception as e:
                logger.error(f"Error creating movement for user {current_user.id}: {e}")
                flash("An unexpected error occurred", "error")

        filtro_tipo = request.args.get("tipo")
        try:
            movements = finance_service.get_movements_with_filter(current_user.id, filtro_tipo)
            summary = finance_service.calculate_financial_summary(current_user.id)
            categorias = finance_service.get_category_totals(current_user.id)
            cuentas = finance_service.get_accounts(current_user.id)
            metas = finance_service.get_goals(current_user.id)
            return render_template(
                "templates/pages/movimientos.html",
                movimientos=movements,
                filtro_tipo=filtro_tipo,
                categorias=categorias,
                cuentas=cuentas,
                metas=metas,
                total_ingresos=summary.total_ingresos,
                total_gastos=summary.total_gastos,
                total_ahorros=summary.total_ahorros,
                saldo_neto=summary.saldo_neto
            )
        except Exception as e:
            logger.error(f"Error loading movements for user {current_user.id}: {e}")
            flash("Error loading movements", "error")
            return render_template("pages/movimientos.html", movimientos=[])

    @main_bp.route("/borrar_movimiento/<int:movement_id>", methods=["POST"])
    @login_required
    def borrar_movimiento(movement_id):
        try:
            success = finance_service.delete_movement(movement_id, current_user.id)
            if success:
                flash("Movement deleted successfully", "success")
            else:
                flash("Movement not found or access denied", "error")
        except Exception as e:
            logger.error(f"Error deleting movement {movement_id} for user {current_user.id}: {e}")
            flash("Error deleting movement", "error")

        return redirect(url_for("main.movimientos"))

    # -------------------------------
    # Notas
    # -------------------------------
    @main_bp.route("/notas", methods=["GET", "POST"])
    @login_required
    def notas():
        if request.method == "POST":
            try:
                fecha = request.form.get("fecha")
                nota_texto = request.form.get("nota")
                if not fecha or not nota_texto:
                    flash("Date and note content are required", "error")
                else:
                    success = notes_service.create_note(current_user.id, fecha, nota_texto)
                    if success:
                        flash("Note created successfully", "success")
                        return redirect(url_for("main.notas"))
                    else:
                        flash("Error creating note", "error")
            except Exception as e:
                logger.error(f"Error creating note for user {current_user.id}: {e}")
                flash("An unexpected error occurred", "error")

        try:
            user_notes = notes_service.get_notes(current_user.id)
            return render_template("pages/notas.html", notas=user_notes)
        except Exception as e:
            logger.error(f"Error loading notes for user {current_user.id}: {e}")
            flash("Error loading notes", "error")
            return render_template("pages/notas.html", notas=[])

    # -------------------------------
    # Perfil
    # -------------------------------
    @main_bp.route("/perfil")
    @login_required
    def perfil():
        return render_template("templates/pages/perfil.html")

    # -------------------------------
    # Settings
    # -------------------------------
    @main_bp.route("/settings")
    @login_required
    def settings():
        return render_template("templates/pages/settings.html")

    # -------------------------------
    # VPS
    # -------------------------------
    @main_bp.route("/vps")
    @login_required
    def vps():
        return render_template("templates/pages/vps.html")

    # -------------------------------
    # Stats
    # -------------------------------
    @main_bp.route("/stats")
    @login_required
    def stats():
        return render_template("templates/pages/stats.html")

    # -------------------------------
    # Ingresos
    # -------------------------------
    @main_bp.route("/ingresos")
    @login_required
    def ingresos():
        return render_template("templates/pages/ingresos.html")

    # -------------------------------
    # Gastos
    # -------------------------------
    @main_bp.route("/gastos")
    @login_required
    def gastos():
        return render_template("templates/pages/gastos.html")

    # -------------------------------
    # API Endpoints
    # -------------------------------
    @main_bp.route("/api/financial-summary")
    @login_required
    def api_financial_summary():
        try:
            summary = finance_service.calculate_financial_summary(current_user.id)
            return jsonify({
                'total_ingresos': summary.total_ingresos,
                'total_gastos': summary.total_gastos,
                'total_ahorros': summary.total_ahorros,
                'saldo_neto': summary.saldo_neto
            })
        except Exception as e:
            logger.error(f"Error getting financial summary for user {current_user.id}: {e}")
            return jsonify({'error': 'Failed to load financial summary'}), 500

    @main_bp.route("/api/top-categories")
    @login_required
    def api_top_categories():
        try:
            limit = request.args.get('limit', 5, type=int)
            categories = finance_service.get_top_expense_categories(current_user.id, limit)
            return jsonify([{
                'categoria': cat.categoria,
                'total': cat.total
            } for cat in categories])
        except Exception as e:
            logger.error(f"Error getting top categories for user {current_user.id}: {e}")
            return jsonify({'error': 'Failed to load top categories'}), 500

    @main_bp.route("/api/account-balances")
    @login_required
    def api_account_balances():
        try:
            balances = finance_service.get_account_balances(current_user.id)
            return jsonify([{
                'cuenta': balance.cuenta,
                'saldo': balance.saldo
            } for balance in balances])
        except Exception as e:
            logger.error(f"Error getting account balances for user {current_user.id}: {e}")
            return jsonify({'error': 'Failed to load account balances'}), 500

    return main_bp
