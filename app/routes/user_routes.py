from flask import Blueprint, request
from app.controllers.user_controller import UserController


user_bp = Blueprint("user", __name__, url_prefix="/user")
controller = UserController()


@user_bp.route("/<document>", methods=["GET"])
def get_user_by_document(document):
    return controller.get_user_by_document(document)
