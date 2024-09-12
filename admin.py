from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import get_db_connection  # Import from db.py

admin = Blueprint('admin', __name__)

# Admin dashboard route
@admin.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('role') != 'admin':
        flash('Access denied! Admins only.', 'danger')
        return redirect(url_for('index'))

    # Fetch some statistics from the database
    conn = get_db_connection()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    # total_uploads = conn.execute('SELECT COUNT(*) FROM uploads').fetchone()[0]
    # total_reports = conn.execute('SELECT COUNT(*) FROM reports').fetchone()[0]
    # recent_uploads = conn.execute('SELECT filename, upload_date, processed, result FROM uploads ORDER BY upload_date DESC LIMIT 5').fetchall()
    conn.close()

    # Pass the data to the dashboard template
    return render_template('admin_dashboard.html', total_users=total_users)
# , total_uploads=total_uploads, total_reports=total_reports, recent_uploads=recent_uploads