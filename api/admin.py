import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.db import get_db_connection
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def check_admin_role():
    if request.method == 'OPTIONS':
        return
        
    from flask_jwt_extended import verify_jwt_in_request
    verify_jwt_in_request()
    
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    if current_user['role'] != 'admin':
        return jsonify({"message": "Admin privileges required"}), 403

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    stats = {
        "users_count": 0,
        "active_lost_count": 0,
        "active_found_count": 0,
        "recovered_count": 0
    }
    
    try:
        # Total users (role = user)
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'user'")
        stats["users_count"] = cursor.fetchone()["count"]
        
        # Active lost items (only 'open')
        cursor.execute("SELECT COUNT(*) as count FROM lost_items WHERE status = 'open'")
        stats["active_lost_count"] = cursor.fetchone()["count"]
        
        # Active found items (only 'open')
        cursor.execute("SELECT COUNT(*) as count FROM found_items WHERE status = 'open'")
        stats["active_found_count"] = cursor.fetchone()["count"]
        
        # Total recovered items (lost + found)
        cursor.execute("SELECT COUNT(*) as count FROM lost_items WHERE status = 'recovered'")
        lost_rec = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM found_items WHERE status = 'recovered'")
        found_rec = cursor.fetchone()["count"]
        
        stats["recovered_count"] = lost_rec + found_rec
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            u.id, 
            u.name, 
            u.email,
            u.created_at,
            (SELECT COUNT(*) FROM lost_items l WHERE l.user_id = u.id) as lost_count,
            (SELECT COUNT(*) FROM found_items f WHERE f.user_id = u.id) as found_count,
            (SELECT COUNT(*) FROM lost_items l WHERE l.user_id = u.id AND l.status = 'recovered') + 
            (SELECT COUNT(*) FROM found_items f WHERE f.user_id = u.id AND f.status = 'recovered') as recovered_count
        FROM users u
        WHERE u.role = 'user'
        ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@admin_bp.route('/delete-user', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"message": "User ID is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Fetch user's item images to delete from filesystem before cascading deletion
        cursor.execute("SELECT image FROM lost_items WHERE user_id = %s", (user_id,))
        lost_images = cursor.fetchall()
        
        cursor.execute("SELECT image FROM found_items WHERE user_id = %s", (user_id,))
        found_images = cursor.fetchall()
        
        for item in lost_images + found_images:
            if item['image']:
                filepath = os.path.join(Config.UPLOAD_FOLDER, item['image'])
                if os.path.exists(filepath):
                    os.remove(filepath)
                    
        # Due to ON DELETE CASCADE, deleting the user will remove their items and matches
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        if cursor.rowcount == 0:
            return jsonify({"message": "User not found"}), 404
            
        conn.commit()
        return jsonify({"message": "User and associated items deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
