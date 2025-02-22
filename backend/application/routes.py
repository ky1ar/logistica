import os, logging

from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from application.controllers import BaseController
from flask_jwt_extended import jwt_required
from flask_socketio import emit, join_room, leave_room
from application import socketio
from config import Config


blueprint = Blueprint("base", __name__)
controller = BaseController()


@blueprint.route("/", methods=["GET"])
def health():
    return {"message": "Logistica Backend API UP",}, 200


@blueprint.route("/user/<document>", methods=["GET"])
def user_get_by_document(document):
    return controller.user_get_by_document(document)


@blueprint.route("/user/login", methods=["POST"])
def user_login():
    return controller.user_login(request.get_json())


@blueprint.route("/user/verify", methods=["GET"])
@jwt_required()
def user_verify():
    return jsonify({"message": "Token válido"}), 200


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


@blueprint.route("/photo/upload", methods=["POST"])
def photo_upload():
    image = request.files["image"]
    order_number = request.form.get("order_number")

    if image.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    filename = secure_filename(f"order_{order_number}_{image.filename}")
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    image.save(filepath)
    data = {
        "order_number": order_number,
        "filepath": filename
    }
    return controller.photo_upload(data)


@blueprint.route("/uploads/<filename>")
def uploads(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@blueprint.route("/order/set", methods=["POST"])
def order_set():
    return controller.order_set(request.get_json())


@blueprint.route("/order/schedule", methods=["GET"])
def order_schedule():
    offset = request.args.get('offset', None)
    return controller.order_schedule(offset)


@blueprint.route("/shipping/day", methods=["GET"])
def shipping_day():
    offset = request.args.get('offset', None)
    return controller.shipping_day(offset)




@socketio.on("connect")
def handle_connect():
    logging.info("Cliente conectado")
    emit("server_response", {"message": "Conectado al servidor"})


@socketio.on("disconnect")
def handle_disconnect():
    logging.info("Cliente desconectado")


@socketio.on("message")
def handle_message(data):
    logging.info(f"Mensaje recibido: {data}")
    emit("server_response", {"message": f"Recibido: {data}"}, broadcast=True)


@socketio.on("update_schedule")
def handle_update(data):
    #controller.send_message(data)
    logging.info("Update_schedule")
    emit("update_schedule", {}, broadcast=True)


@socketio.on("on_the_way")
def handle_on_the_way(data):
    controller.send_message(data)
    #logging.info(f"Mensaje recibido: {phone}")
    #emit("update_schedule", {}, broadcast=True)
    