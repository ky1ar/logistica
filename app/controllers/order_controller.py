import logging

from app.services.order_service import OrderService
from app.services.user_service import UserService
from app.services.utils_service import handle_logs_and_exceptions, validate_request

class OrderController:
    def __init__(self):
        self.service = OrderService()
        self.user = UserService()


    @handle_logs_and_exceptions
    def order_get_by_number(self, number):
        order, order_status = self.service.get_order_by_number(number)
        if order_status != 200:
            return order, order_status
        
        result = order.to_dict()
        result.update({
            "client_name": order.client.name,
            "district_name": order.district.name,
            "driver_name": order.driver.name,
            "shipping_type_name": order.shipping_type.name,
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
            {"purchase_order_number", "shipping_type_id", "driver_id", "admin_id" ,"address" ,"district_id" ,"creation_date" ,"comments"}
        ):
            return validation_error, 400

        number = request.get("purchase_order_number").strip()
        shipping_type = request.get("shipping_type_id")

        if not number:
            return "El número de orden no puede estar vacío", 400

        if not shipping_type:
            return "Seleccione un tipo de envío", 400
        
        get_order, get_order_status = self.service.get_order_by_number(number)
        if get_order_status == 500:
            return get_order, get_order_status

        if get_order_status == 200:
            return "Este número de orden ya ha sido registrado", 400
        

        client_id = request.get("client_id")
        if not client_id:
            client = request.pop("client")

            document = client.get("document")
            get_user, get_user_status = self.user.get_user_by_document(document)
            if get_user_status == 500:
                return get_user, get_user_status

            if get_user_status == 200:
                return "El documento de este cliente ya se encuentra registrado", 400
            
            added_client, added_client_status = self.user.add_client(client)
            if added_client_status != 200:
                return added_client, added_client_status
            
            request["client_id"] = added_client

        return self.service.add_order(request)


    @handle_logs_and_exceptions
    def order_set(self, request):
        if validation_error := validate_request(
            request, 
            {"purchase_order_number", "shipping_date", "shipping_schedule_id", "admin_id", "shipping_status_id"}
        ):
            return validation_error, 400

        number = request.get("purchase_order_number")
        order, order_status = self.service.get_order_by_number(number)
        if order_status != 200:
            return order, order_status
        
        return self.service.set_order(order, request)


    @handle_logs_and_exceptions
    def order_schedule(self, offset=0):
        return self.service.get_schedule(int(offset))
