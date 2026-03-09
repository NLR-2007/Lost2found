from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.db import get_db_connection

match_bp = Blueprint('match', __name__)

@match_bp.route('/matches', methods=['GET'])
@jwt_required()
def get_matches():
    # Both normal users and admins can hit this endpoint for simplicity as per requirements, 
    # but the frontend will only surface this data / page to admins.
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Find combination of lost and found items sharing category and location and status = 'open'
        query = """
        SELECT 
            l.id as lost_id, 
            l.item_name as lost_item_name, 
            f.id as found_id, 
            f.item_name as found_item_name, 
            l.category, 
            l.location
        FROM lost_items l
        JOIN found_items f 
          ON lower(trim(l.category)) = lower(trim(f.category)) 
         AND lower(trim(l.location)) = lower(trim(f.location))
        WHERE l.status = 'open' AND f.status = 'open'
        """
        cursor.execute(query)
        matches = cursor.fetchall()
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@match_bp.route('/confirm-match', methods=['POST'])
@jwt_required()
def confirm_match():
    import json
    jwt_id = get_jwt_identity()
    current_user = json.loads(jwt_id) if isinstance(jwt_id, str) else jwt_id
    if current_user['role'] != 'admin':
        return jsonify({"message": "Admin privileges required"}), 403
        
    data = request.get_json()
    lost_id = data.get('lost_id')
    found_id = data.get('found_id')
    
    if not lost_id or not found_id:
        return jsonify({"message": "Both lost_id and found_id are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure they are currently 'open'
        cursor.execute("SELECT status FROM lost_items WHERE id = %s", (lost_id,))
        lost_item = cursor.fetchone()
        cursor.execute("SELECT status FROM found_items WHERE id = %s", (found_id,))
        found_item = cursor.fetchone()
        
        if not lost_item or not found_item:
            return jsonify({"message": "One or both items not found"}), 404
            
        if lost_item[0] != 'open' or found_item[0] != 'open':
            return jsonify({"message": "Both items must be open to confirm a match"}), 400

        # Insert match record
        cursor.execute(
            "INSERT INTO matches (lost_id, found_id) VALUES (%s, %s)",
            (lost_id, found_id)
        )
        
        # Update statuses to 'matched'
        cursor.execute("UPDATE lost_items SET status = 'matched' WHERE id = %s", (lost_id,))
        cursor.execute("UPDATE found_items SET status = 'matched' WHERE id = %s", (found_id,))
        
        conn.commit()
        return jsonify({"message": "Match confirmed and statuses updated"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
