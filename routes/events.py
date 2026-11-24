from flask import Blueprint, request, jsonify
from models import db, Event, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/api/events')

@events_bp.route('', methods=['GET'])
def get_events():
    """Get all events that the user can see"""
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events]), 200

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get a specific event by event_id"""
    event = Event.query.get_or_404(event_id)
    return jsonify(event.to_dict()), 200

@events_bp.route('', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event (requires authentication)"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    if not data.get('date'):
        return jsonify({'error': 'Date is required'}), 400
    
    # Parse date string to datetime
    try:
        event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return jsonify({'error': 'Invalid date format. Use ISO 8601 format (e.g., 2024-01-15T18:00:00)'}), 400
    
    user_id = int(get_jwt_identity())
    
    event = Event(
        title=data['title'],
        description=data.get('description'),
        date=event_date,
        location=data.get('location'),
        capacity=data.get('capacity'),  # None means unlimited
        is_public=data.get('is_public', True),
        requires_admin=data.get('requires_admin', False),
        created_by=user_id
    )
    
    db.session.add(event)
    db.session.commit()
    
    return jsonify(event.to_dict()), 201

