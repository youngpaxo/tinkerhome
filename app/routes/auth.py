from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.services import UserService
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def init_auth_routes(user_service: UserService):
    """Initialize authentication routes with dependency injection"""
    
    @auth_bp.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            
            if not username or not password:
                flash("Username and password are required", "error")
                return render_template("pages/register.html")
            
            try:
                user_id = user_service.create_user(username, password)
                if user_id:
                    flash("User created successfully! Please log in.", "success")
                    return redirect(url_for("auth.login"))
                else:
                    flash("Failed to create user", "error")
            except ValueError as e:
                flash(str(e), "error")
            except Exception as e:
                logger.error(f"Unexpected error during registration: {e}")
                flash("An unexpected error occurred", "error")
        
        return render_template("pages/register.html")
    
    @auth_bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            
            if not username or not password:
                flash("Username and password are required", "error")
                return render_template("pages/login.html")
            
            user = user_service.authenticate_user(username, password)
            if user:
                login_user(user)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for("main.index"))
            else:
                flash("Invalid username or password", "error")
        
        return render_template("pages/login.html")
    
    @auth_bp.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out", "info")
        return redirect(url_for("auth.login"))
    
    return auth_bp