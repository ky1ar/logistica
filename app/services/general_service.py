import logging

from app.models.models import Drivers, Districts, ShippingTypes
from app.services.utils_service import handle_exceptions, handle_db_exceptions
from flask import g


class GeneralService:


    @handle_db_exceptions
    def get_drivers(self):
        drivers = g.db_session.query(Drivers).all()
        if not drivers:
            return 'Drivers not found', 400
        
        return [driver.to_dict() for driver in drivers], 200
    

    @handle_db_exceptions
    def get_districts(self):
        districts = g.db_session.query(Districts).all()
        if not districts:
            return 'Districts not found', 400
        
        return [district.to_dict() for district in districts], 200


    @handle_db_exceptions
    def get_shipping_types(self):
        shipping_types = g.db_session.query(ShippingTypes).all()
        if not shipping_types:
            return 'Shipping Types not found', 400
        
        return [shipping_type.to_dict() for shipping_type in shipping_types], 200