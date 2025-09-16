"""
Clothing API endpoints
"""

from flask import Blueprint, jsonify, request
import os

clothing_bp = Blueprint('clothing', __name__)

# Sample clothing data
SAMPLE_CLOTHING = [
    {
        'id': 1,
        'name': 'Classic T-Shirt',
        'price': 29.99,
        'image': '/static/images/sample-tshirt.svg',
        'category': 'tops',
        'sizes': ['XS', 'S', 'M', 'L', 'XL'],
        'colors': ['Blue', 'Red', 'White', 'Black'],
        'description': 'Comfortable cotton t-shirt perfect for everyday wear'
    },
    {
        'id': 2,
        'name': 'Cozy Hoodie',
        'price': 59.99,
        'image': '/static/images/sample-hoodie.svg',
        'category': 'tops',
        'sizes': ['S', 'M', 'L', 'XL', 'XXL'],
        'colors': ['Brown', 'Gray', 'Navy', 'Black'],
        'description': 'Warm and comfortable hoodie with kangaroo pocket'
    },
    {
        'id': 3,
        'name': 'Summer Dress',
        'price': 79.99,
        'image': '/static/images/sample-dress.svg',
        'category': 'dresses',
        'sizes': ['XS', 'S', 'M', 'L'],
        'colors': ['Pink', 'Blue', 'White', 'Yellow'],
        'description': 'Elegant summer dress for special occasions'
    },
    {
        'id': 4,
        'name': 'Leather Jacket',
        'price': 129.99,
        'image': '/static/images/sample-jacket.svg',
        'category': 'outerwear',
        'sizes': ['S', 'M', 'L', 'XL'],
        'colors': ['Black', 'Brown', 'Navy'],
        'description': 'Stylish leather jacket for a modern look'
    }
]

@clothing_bp.route('/featured', methods=['GET'])
def get_featured_clothing():
    """Get featured clothing items"""
    try:
        # Return first 3 items as featured
        featured_items = SAMPLE_CLOTHING[:3]
        return jsonify({
            'success': True,
            'data': featured_items,
            'count': len(featured_items)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clothing_bp.route('/<int:item_id>', methods=['GET'])
def get_clothing_item(item_id):
    """Get specific clothing item by ID"""
    try:
        # Find item by ID
        item = next((item for item in SAMPLE_CLOTHING if item['id'] == item_id), None)
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Clothing item not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clothing_bp.route('/', methods=['GET'])
def get_all_clothing():
    """Get all clothing items with optional filtering"""
    try:
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        items = SAMPLE_CLOTHING.copy()
        
        # Apply filters
        if category:
            items = [item for item in items if item['category'].lower() == category.lower()]
        
        if min_price is not None:
            items = [item for item in items if item['price'] >= min_price]
        
        if max_price is not None:
            items = [item for item in items if item['price'] <= max_price]
        
        return jsonify({
            'success': True,
            'data': items,
            'count': len(items),
            'filters': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clothing_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all available clothing categories"""
    try:
        categories = list(set(item['category'] for item in SAMPLE_CLOTHING))
        return jsonify({
            'success': True,
            'data': categories,
            'count': len(categories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clothing_bp.route('/<int:item_id>/try-on', methods=['POST'])
def try_on_clothing(item_id):
    """Initiate virtual try-on for a clothing item"""
    try:
        # Find item by ID
        item = next((item for item in SAMPLE_CLOTHING if item['id'] == item_id), None)
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Clothing item not found'
            }), 404
        
        # Get request data
        data = request.get_json()
        size = data.get('size', 'M')
        color = data.get('color', item['colors'][0])
        
        # Simulate try-on process
        return jsonify({
            'success': True,
            'data': {
                'item_id': item_id,
                'item_name': item['name'],
                'selected_size': size,
                'selected_color': color,
                'try_on_status': 'ready',
                'confidence': 0.95,
                'recommendations': {
                    'size_fit': 'good',
                    'style_match': 'excellent',
                    'alternative_sizes': ['S', 'L'] if size == 'M' else ['M']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
