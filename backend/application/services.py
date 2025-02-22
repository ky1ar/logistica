import logging

from config import Twilio
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from datetime import date, datetime, timezone, timedelta
from application.models import Users, PurchaseOrders, Drivers, Districts, ShippingTypes
from application.handlers import handle_exceptions, handle_db_exceptions
from sqlalchemy.orm import joinedload
from sqlalchemy import asc
from flask import g

logging.getLogger("twilio").setLevel(logging.ERROR)

class BaseService:

    def __init__(self):
        #self.sms_repository = SmsRepository()
        self.client = Client(Twilio.ACCOUNT_SID, Twilio.AUTH_TOKEN)


    @handle_exceptions
    def send_message(self, data, template):
        phone = data.get("phone")
        user = data.get("user")
        file = data.get("file")

        messages = {
            3: f"Hola {user},\n\n📦 Tu pedido está en camino. 🚀\nNuestro repartidor ya está en ruta hacia la dirección indicada. Te avisaremos cuando haya sido entregado.\n\n¡Gracias por tu compra! 😊",
            4: f"Hola {user},\n\n✅ Tu pedido ha sido entregado con éxito. 🎉\nEsperamos que disfrutes tu compra. Si tienes alguna pregunta o inconveniente, no dudes en contactarnos.\n\n¡Gracias por confiar en nosotros! 🛍️",
            6: f"Hola {user},\n\n⚠️ No hemos podido entregar tu pedido. 😔\nPor favor, contáctanos para coordinar una nueva entrega o más detalles sobre el estado de tu pedido.\n\nLamentamos el inconveniente y agradecemos tu paciencia. 🙏"
        }

        message_body = messages.get(template, "Hola, tu pedido ha sido actualizado. 📦")  # Mensaje por defecto

        try:
            media_url = None
            if template == 4:
                media_url = f"https://logistica.munoz.pe/api/uploads/{file}"
                
            message = self.client.messages.create(
                from_=f"whatsapp:{Twilio.PHONE}",
                body=message_body,
                to=f"whatsapp:+{phone}",
                media_url=[media_url] if media_url else None
            )
            logging.info(message)
        except TwilioRestException as e:
            logging.error(f"Error al enviar SMS: {e.msg}", exc_info=True)
            return e.msg, e.status

        return "Message sent successfully", 200

    

    @handle_db_exceptions
    def get_user_by_email(self, email):
        user = g.db_session.query(Users).filter_by(email=email).first()
        if not user:
            return 'Usuario no encontrado', 400
        
        #user_data = user.to_dict()
        #fields_to_remove = ['password', 'role', 'image', 'nick', 'stamp'] 

        #for field in fields_to_remove:
        #    user_data.pop(field, None) 

        return user, 200


    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'User not found', 400
        
        user_data = user.to_dict()
        fields_to_remove = ['password', 'role', 'image', 'nick', 'stamp'] 

        for field in fields_to_remove:
            user_data.pop(field, None) 

        return user_data, 200


    @handle_db_exceptions
    def add_client(self, client):
        utc_now = datetime.now(timezone.utc)
        peru_time = utc_now - timedelta(hours=5)

        new_client = Users(
            levels=1,
            document=client.get("document"),
            name=client.get("name"),
            email=client.get("email"),
            phone=client.get("phone"),
            password="password",
            stamp=peru_time,
        )

        g.db_session.add(new_client)
        g.db_session.flush()
        client_id = new_client.id
        g.db_session.commit()
        logging.info(f"New client added to DB with id {client_id}")
        return client_id, 200
    

    @handle_db_exceptions
    def get_order_by_number(self, number):
        purchase_order = (
            g.db_session.query(PurchaseOrders)
            .filter_by(number=number)
            .options(
                joinedload(PurchaseOrders.client),
                joinedload(PurchaseOrders.district),
                joinedload(PurchaseOrders.driver),
                joinedload(PurchaseOrders.shipping_type)
            )
            .first()
        )
            
        if not purchase_order:
            return 'Orden de pedido no encontrada', 400
        
        return purchase_order, 200
 

    
    @handle_db_exceptions
    def get_orders_by_status(self, status):
        purchase_orders = g.db_session.query(PurchaseOrders).filter_by(shipping_status_id=status).order_by(asc(PurchaseOrders.creation_date)).all()
        if not purchase_orders:
            return 'No se encontraron ordenes de pedido para este estado', 400
        
        result = []
        for purchase_order in purchase_orders:
            creation_date = purchase_order.creation_date.strftime("%Y-%m-%d")

            order_data = {
                "address": purchase_order.address,
                "client_name": purchase_order.client.name.title(),
                "creation_date": creation_date,
                "district_name": purchase_order.district.name,
                "number": purchase_order.number,
                "shipping_type_name": purchase_order.shipping_type.name,
                "shipping_type_slug": purchase_order.shipping_type.slug,
            }

            result.append(order_data)

        return result, 200
    

    @handle_db_exceptions
    def add_order(self, data):
        #utc_now = datetime.now(timezone.utc)
        #peru_time = utc_now - timedelta(hours=5)

        new_purchase_order = PurchaseOrders(
            number=data.get("purchase_order_number"),
            client_id=data.get("client_id"),
            shipping_type_id=data.get("shipping_type_id"),
            driver_id=data.get("driver_id"),
            admin_id=data.get("admin_id"),
            address=data.get("address"),
            district_id=data.get("district_id"),
            creation_date=data.get("creation_date"),
            comments=data.get("comments"),
            shipping_status_id=1,
            send_email=data.get("send_email"),
        )

        g.db_session.add(new_purchase_order)
        g.db_session.commit()
        logging.info("New purchase rder added to DB")
        return "Orden registrada correctamente", 200


    @handle_db_exceptions
    def set_order(self, order, data):
        if "shipping_date" in data:
            order.shipping_date = data["shipping_date"]
        if "shipping_status_id" in data:
            order.shipping_status_id = data["shipping_status_id"]
        if "shipping_schedule_id" in data:
            order.shipping_schedule_id = data["shipping_schedule_id"]
        if "filepath" in data:
            order.image_path = data["filepath"]

        g.db_session.add(order)
        g.db_session.commit()
        return "Orden actualizada correctamente", 200
    

    @handle_db_exceptions
    def get_scheduled_orders(self, start_date, end_date):
        purchase_orders = (
            g.db_session.query(PurchaseOrders)
            .filter(PurchaseOrders.shipping_date >= start_date, PurchaseOrders.shipping_date <= end_date)
            .filter(PurchaseOrders.shipping_status_id != 1)
            .all()
        )
        
        result = []
        if not purchase_orders:
            return result, 200
        
        for purchase_order in purchase_orders:
            creation_date = purchase_order.creation_date.strftime("%Y-%m-%d")
            shipping_date = purchase_order.shipping_date.strftime("%Y-%m-%d")


            order_data = {
                "address": purchase_order.address,
                "client_name": purchase_order.client.name.title(),
                "client_phone": purchase_order.client.phone,
                "creation_date": creation_date,
                "shipping_date": shipping_date,
                "district_name": purchase_order.district.name,
                "number": purchase_order.number,
                "shipping_type_name": purchase_order.shipping_type.name,
                "shipping_type_slug": purchase_order.shipping_type.slug,
                "shipping_schedule_name": purchase_order.shipping_schedule.name,
                "schedule": purchase_order.shipping_schedule_id,
                "shipping_status_id": purchase_order.shipping_status_id,
                "shipping_status_name": purchase_order.shipping_status.name,
                "send_email": purchase_order.send_email
            }

            result.append(order_data)

        return result, 200
    

    @handle_db_exceptions
    def get_schedule(self, offset):
        DAYS_IN_SPANISH = {
            "Monday": "lun",
            "Tuesday": "mar",
            "Wednesday": "mié",
            "Thursday": "jue",
            "Friday": "vie",
            "Saturday": "sáb",
            "Sunday": "dom"
        }

        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        start_date += timedelta(weeks=offset)
        end_date += timedelta(weeks=offset)

        scheduled_orders, scheduled_orders_status = self.get_scheduled_orders(start_date, end_date)
        if scheduled_orders_status != 200:
            return scheduled_orders, scheduled_orders_status
        
        schedule_by_day = []
        for i in range(6):
            day = start_date + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_name = day.strftime("%A")
            day_name_es = DAYS_IN_SPANISH.get(day_name, day_name)

            day_name_with_number = f"{day_name_es} {day.day}"

            day_orders = [order for order in scheduled_orders if order['shipping_date'] == day_str]

            schedule_orders = {1: [], 2: []}
            for order in day_orders:
                schedule_orders.setdefault(order["schedule"], []).append(order)
                
            schedule_by_day.append({
                "date": day_str,
                "day_name": day_name_with_number,
                "orders": {
                    "schedule_1": schedule_orders.get(1, []),
                    "schedule_2": schedule_orders.get(2, [])
                }
            })

        return schedule_by_day, 200
    

    @handle_db_exceptions
    def get_day_shippings(self, offset):
        DAYS_IN_SPANISH = {
            "Monday": "lunes",
            "Tuesday": "martes",
            "Wednesday": "miércoles",
            "Thursday": "jueves",
            "Friday": "viernes",
            "Saturday": "sábado",
            "Sunday": "domingo"
        }

        today = date.today()
        day_of_interest = today + timedelta(days=offset)
        day_str = day_of_interest.strftime("%Y-%m-%d")
        day_name = day_of_interest.strftime("%A")
        day_name_es = DAYS_IN_SPANISH.get(day_name, day_name)
        day_name_with_number = f"{day_name_es} {day_of_interest.day}"

        scheduled_orders, scheduled_orders_status = self.get_scheduled_orders(day_of_interest, day_of_interest)
        if scheduled_orders_status != 200:
            return scheduled_orders, scheduled_orders_status
        
        day_orders = [order for order in scheduled_orders if order['shipping_date'] == day_str]

        schedule_orders = {1: [], 2: []}
        for order in day_orders:
            schedule_orders.setdefault(order["schedule"], []).append(order)

        return {
            "date": day_str,
            "day_name": day_name_with_number,
            "orders": {
                "schedule_1": schedule_orders.get(1, []),
                "schedule_2": schedule_orders.get(2, [])
            }
        }, 200


    @handle_db_exceptions
    def get_drivers(self):
        drivers = g.db_session.query(Drivers).all()
        if not drivers:
            return 'Drivers not found', 400
        
        return [driver.to_dict() for driver in drivers], 200
    

    @handle_db_exceptions
    def get_districts(self):
        districts = g.db_session.query(Districts).order_by(Districts.name).all()
        if not districts:
            return 'Districts not found', 400
        
        return [district.to_dict() for district in districts], 200


    @handle_db_exceptions
    def get_shipping_types(self):
        shipping_types = g.db_session.query(ShippingTypes).all()
        if not shipping_types:
            return 'Shipping Types not found', 400
        
        return [shipping_type.to_dict() for shipping_type in shipping_types], 200