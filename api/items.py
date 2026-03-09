import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import time
import random
from datetime import datetime, date
from config import Config
from api.db import get_db_connection

items_bp = Blueprint('items', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(file):
    if not file or not allowed_file(file.filename):
        return None
    
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > Config.MAX_CONTENT_LENGTH:
        return 'TOO_LARGE'

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filename

def serialize_item(item):
    """Convert datetime objects in a DB row dict to plain strings (YYYY-MM-DD HH:MM:SS)
    so Flask doesn't auto-convert them to RFC/GMT format which confuses the browser."""
    result = {}
    for key, value in item.items():
        if isinstance(value, datetime):
            result[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, date):
            result[key] = value.strftime('%Y-%m-%d')
        else:
            result[key] = value
    return result

@items_bp.route('/lost', methods=['POST'])
@jwt_required()
def report_lost():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    user_id = current_user['id']
    
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    description = request.form.get('description', '')
    location = request.form.get('location')
    mobile = request.form.get('mobile')
    college_id = request.form.get('college_id')
    
    if not all([item_name, category, location, mobile, college_id]):
        return jsonify({"message": "All required fields must be filled"}), 400
        
    if len(mobile) != 10 or not mobile.isdigit():
        return jsonify({"message": "Mobile number must be exactly 10 digits"}), 400
        
    image_file = request.files.get('image')
    image_filename = None
    if image_file:
        image_filename = save_image(image_file)
        if image_filename == 'TOO_LARGE':
            return jsonify({"message": "Image size exceeds 5MB limit"}), 400
        if not image_filename:
            return jsonify({"message": "Invalid image format. Allowed: jpg, jpeg, png"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO lost_items 
               (user_id, item_name, category, description, location, image, mobile, college_id, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, item_name, category, description, location, image_filename, mobile, college_id, 'open')
        )
        conn.commit()
        return jsonify({"message": "Lost item reported successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@items_bp.route('/found', methods=['POST'])
@jwt_required()
def report_found():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    user_id = current_user['id']
    
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    description = request.form.get('description', '')
    location = request.form.get('location')
    mobile = request.form.get('mobile')
    college_id = request.form.get('college_id')
    
    if not all([item_name, category, location, mobile, college_id]):
        return jsonify({"message": "All required fields must be filled"}), 400
        
    if len(mobile) != 10 or not mobile.isdigit():
        return jsonify({"message": "Mobile number must be exactly 10 digits"}), 400
        
    image_file = request.files.get('image')
    image_filename = None
    if image_file:
        image_filename = save_image(image_file)
        if image_filename == 'TOO_LARGE':
            return jsonify({"message": "Image size exceeds 5MB limit"}), 400
        if not image_filename:
            return jsonify({"message": "Invalid image format. Allowed: jpg, jpeg, png"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO found_items 
               (user_id, item_name, category, description, location, image, mobile, college_id, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, item_name, category, description, location, image_filename, mobile, college_id, 'open')
        )
        conn.commit()
        return jsonify({"message": "Found item reported successfully"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@items_bp.route('/items', methods=['GET'])
@jwt_required()
def get_all_items():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT l.*, u.name as user_name, u.email as user_email, 'lost' as type
            FROM lost_items l 
            JOIN users u ON l.user_id = u.id
            ORDER BY l.created_at DESC
        """)
        lost_items = [serialize_item(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT f.*, u.name as user_name, u.email as user_email, 'found' as type
            FROM found_items f 
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
        """)
        found_items = [serialize_item(row) for row in cursor.fetchall()]
        
        return jsonify({"lost": lost_items, "found": found_items}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@items_bp.route('/my-items', methods=['GET'])
@jwt_required()
def get_my_items():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    user_id = current_user['id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT l.*, u.name as user_name, u.email as user_email, 'lost' as type
            FROM lost_items l 
            JOIN users u ON l.user_id = u.id
            WHERE l.user_id = %s
            ORDER BY l.created_at DESC
        """, (user_id,))
        lost_items = [serialize_item(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT f.*, u.name as user_name, u.email as user_email, 'found' as type
            FROM found_items f 
            JOIN users u ON f.user_id = u.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """, (user_id,))
        found_items = [serialize_item(row) for row in cursor.fetchall()]
        
        return jsonify({"lost": lost_items, "found": found_items}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@items_bp.route('/update-status', methods=['POST'])
@jwt_required()
def update_status():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    if current_user['role'] != 'admin':
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    item_id = data.get('item_id')
    item_type = data.get('type')
    new_status = data.get('status')
    
    if not all([item_id, item_type, new_status]):
        return jsonify({"message": "Missing required fields"}), 400
        
    if item_type not in ['lost', 'found'] or new_status not in ['open', 'matched', 'recovered']:
        return jsonify({"message": "Invalid type or status"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    table = 'lost_items' if item_type == 'lost' else 'found_items'
    
    try:
        if new_status == 'recovered':
            cursor.execute(f"UPDATE {table} SET status = %s, recovered_at = CURRENT_TIMESTAMP WHERE id = %s", (new_status, item_id))
        else:
            cursor.execute(f"UPDATE {table} SET status = %s, recovered_at = NULL WHERE id = %s", (new_status, item_id))
        
        if cursor.rowcount == 0:
            return jsonify({"message": "Item not found"}), 404
            
        conn.commit()
        return jsonify({"message": "Status updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@items_bp.route('/delete-item', methods=['DELETE'])
@jwt_required()
def delete_item():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    
    item_id = request.args.get('item_id')
    item_type = request.args.get('type')
    
    if not item_id or not item_type or item_type not in ['lost', 'found']:
        return jsonify({"message": "Invalid request"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    table = 'lost_items' if item_type == 'lost' else 'found_items'
    
    try:
        cursor.execute(f"SELECT user_id, image FROM {table} WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            return jsonify({"message": "Item not found"}), 404
            
        if current_user['role'] != 'admin' and item['user_id'] != current_user['id']:
            return jsonify({"message": "Permission denied"}), 403
            
        match_table_col = 'lost_id' if item_type == 'lost' else 'found_id'
        cursor.execute(f"DELETE FROM matches WHERE {match_table_col} = %s", (item_id,))
        
        if item['image']:
            filepath = os.path.join(Config.UPLOAD_FOLDER, item['image'])
            if os.path.exists(filepath):
                os.remove(filepath)
                
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (item_id,))
        conn.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()