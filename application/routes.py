from flask import Blueprint, request
from application.controllers import BaseController


blueprint = Blueprint("base", __name__)
controller = BaseController()


@blueprint.route("/", methods=["GET"])
def health():
    return {
        "message": "Logistica Backend API UP",
    }, 200


@blueprint.route("/user/<document>", methods=["GET"])
def user_get_by_document(document):
    return controller.user_get_by_document(document)


@blueprint.route("/general/drivers", methods=["GET"])
def general_drivers():
    return controller.general_drivers()


@blueprint.route("/general/districts", methods=["GET"])
def general_districts():
    return controller.general_districts()


@blueprint.route("/general/shipping_types", methods=["GET"])
def general_shipping_types():
    return controller.general_shipping_types()


@blueprint.route("/order/add", methods=["POST"])
def order_add():
    return controller.order_add(request.get_json())


@blueprint.route("/order/<number>", methods=["GET"])
def order_get_by_number(number):
    return controller.order_get_by_number(number)


@blueprint.route("/order/pending", methods=["GET"])
def order_get_pending():
    return controller.order_get_pending()


@blueprint.route("/order/set", methods=["POST"])
def order_set():
    return controller.order_set(request.get_json())


@blueprint.route("/order/schedule", methods=["GET"])
def order_schedule():
    offset = request.args.get('offset', None)
    return controller.order_schedule(offset)
