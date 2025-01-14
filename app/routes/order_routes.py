from flask import Blueprint, request
from app.controllers.order_controller import OrderController


order_bp = Blueprint("order", __name__, url_prefix="/order")
controller = OrderController()


@order_bp.route("/add", methods=["POST"])
def order_add():
    return controller.order_add(request.get_json())


@order_bp.route("/<number>", methods=["GET"])
def order_get_by_number(number):
    return controller.order_get_by_number(number)


@order_bp.route("/pending", methods=["GET"])
def order_get_pending():
    return controller.order_get_pending()


@order_bp.route("/set", methods=["POST"])
def order_set():
    return controller.order_set(request.get_json())


@order_bp.route("/schedule", methods=["GET"])
def order_schedule():
    offset = request.args.get('offset', None)
    return controller.order_schedule(offset)
