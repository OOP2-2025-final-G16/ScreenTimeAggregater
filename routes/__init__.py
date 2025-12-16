from .auth import auth_bp
from .user import user_bp
from .product import product_bp
from .order import order_bp

blueprints = [
    auth_bp,
    user_bp,
    product_bp,
    order_bp,
]
