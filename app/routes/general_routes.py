from flask import Blueprint, request
from app.controllers.general_controller import GeneralController


general_bp = Blueprint("general", __name__, url_prefix="/general")
controller = GeneralController()


@general_bp.route("/drivers", methods=["GET"])
def general_drivers():
    return controller.general_drivers()


@general_bp.route("/districts", methods=["GET"])
def general_districts():
    return controller.general_districts()


@general_bp.route("/shipping_types", methods=["GET"])
def general_shipping_types():
    return controller.general_shipping_types()