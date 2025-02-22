import logging, re

from application import bcrypt
from application.services import BaseService
from application.handlers import handle_logs_and_exceptions, validate_request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

class BaseController:
    def __init__(self):
        self.service = BaseService()     



    @handle_logs_and_exceptions
    def send_message(self, data):
        return self.service.send_message(data, template=3)


    @handle_logs_and_exceptions
    def user_get_by_document(self, document):
        if not document:
            return 'Missing document', 400
        
        return self.service.get_user_by_document(document)
    

    @handle_logs_and_exceptions
    def general_drivers(self):
        return self.service.get_drivers()
    

    @handle_logs_and_exceptions
    def general_districts(self):
        return self.service.get_districts()
    
    @handle_logs_and_exceptions
    def general_shipping_types(self):
        return self.service.get_shipping_types()
    

    @handle_logs_and_exceptions
    def order_get_by_number(self, number):
        order, order_status = self.service.get_order_by_number(number)
        if order_status != 200:
            return order, order_status
        
        result = order.to_dict()
        result.update({
            "client_name": order.client.name,
            "client_document": order.client.document,
            "client_email": order.client.email,
            "client_phone": order.client.phone,
            "client_document_id": order.client.id,
            "district_name": order.district.name,
            "driver_name": order.driver.name,
            "shipping_type_name": order.shipping_type.name,
            "creation_date_format": order.creation_date.strftime("%Y-%m-%d")
        })
        return result, 200
        

    @handle_logs_and_exceptions
    def order_get_pending(self):
        orders, orders_status = self.service.get_orders_by_status(status=1)
        if orders_status != 200:
            return orders, orders_status
        
        return orders, 200


    @handle_logs_and_exceptions
    def order_add(self, request):
        if validation_error := validate_request(
            request, 
            {"purchase_order_number", "shipping_type_id", "driver_id", "admin_id" ,"address" ,"district_id" ,"creation_date" ,"send_email", "comments"}
        ):
            return validation_error, 400

        number = request.get("purchase_order_number")
        shipping_type = request.get("shipping_type_id")
        creation_date = request.get("creation_date")
        district_id = request.get("district_id")
        address = request.get("address")

        if not number.strip():
            return "Ingrese el número de orden", 400

        get_order, get_order_status = self.service.get_order_by_number(number)
        if get_order_status == 500:
            return get_order, get_order_status

        if get_order_status == 200:
            return "Este número de orden ya ha sido registrado", 400
        
        if not shipping_type:
            return "Seleccione un tipo de envío", 400
        
        if not creation_date:
            return "Ingrese la fecha de creación", 400
        
        client_id = request.get("client_id")
        if not client_id:
            client = request.pop("client")
            document = client.get("document")
            email = client.get("email")
            name = client.get("name")
            phone = client.get("phone")

            if not document.strip():
                return "Ingrese el documento", 400

            if not bool(re.fullmatch(r'\d{8}|\d{11}', document)):
                return "Ingrese un documento válido", 400
            
            if not name.strip():
                return "Ingrese el nombre/Razón Social", 400
            
            if not email.strip():
                return "Ingrese el email", 400
            
            if not phone.strip():
                return "Ingrese el teléfono", 400
            
            get_user, get_user_status = self.service.get_user_by_document(document)
            if get_user_status == 500:
                return get_user, get_user_status

            if get_user_status == 200:
                return "El documento ya se encuentra registrado", 400
            
            added_client, added_client_status = self.service.add_client(client)
            if added_client_status != 200:
                return added_client, added_client_status
            
            request["client_id"] = added_client

        if not address.strip():
            return "Ingrese la dirección", 400
        
        if not district_id:
            return "Seleccione un distrito", 400
        
        return self.service.add_order(request)


    @handle_logs_and_exceptions
    def photo_upload(self, request):
        if validation_error := validate_request(
            request, 
            {"order_number", "filepath"}
        ):
            return validation_error, 400

        number = request.pop("order_number")
        order, order_status = self.service.get_order_by_number(number)
        if order_status != 200:
            return order, order_status
        
        return self.service.set_order(order, request)


    @handle_logs_and_exceptions
    def order_set(self, request):
        if validation_error := validate_request(
            request, 
            {"purchase_order_number", "admin_id"}
        ):
            return validation_error, 400

        number = request.get("purchase_order_number")
        shipping_status_id = request.get("shipping_status_id")

        order, order_status = self.service.get_order_by_number(number)
        if order_status != 200:
            return order, order_status
        
        if shipping_status_id == 4 or shipping_status_id == 6:
            data = {
                "phone": order.client.phone,
                "user": order.client.name,
                "file": order.image_path
            }

            self.service.send_message(data,template=shipping_status_id)
        
        return self.service.set_order(order, request)


    @handle_logs_and_exceptions
    def order_schedule(self, offset=0):
        return self.service.get_schedule(int(offset))
    

    @handle_logs_and_exceptions
    def shipping_day(self, offset=0):
        return self.service.get_day_shippings(int(offset))
    
    
    @handle_logs_and_exceptions
    def user_login(self, request):
        if validation_error := validate_request(
            request, 
            {"email", "password"}
        ):
            return validation_error, 400
        
        email = request.get("email")
        password = request.get("password")
        user, user_status = self.service.get_user_by_email(email)
        if user_status != 200:
            return user, user_status
        logging.info(user.to_dict())
        if bcrypt.check_password_hash(user.password.encode('utf-8'), password.encode('utf-8')):
            access_token = create_access_token(identity=str(user.id))

            data = user.to_dict()
            response = {
                "token": access_token,
                "user_id": data["id"],
                "level": data["levels"],
                "name": data["name"],
                "role": data["role"],
                "document": data["document"],
            }
            return response, 200
        

        return "Contraseña incorrecta", 400