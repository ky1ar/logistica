import logging

from app.services.general_service import GeneralService
from app.services.utils_service import handle_logs_and_exceptions

class GeneralController:
    def __init__(self):
        self.service = GeneralService()     

    
    @handle_logs_and_exceptions
    def general_drivers(self):
        return self.service.get_drivers()
    

    @handle_logs_and_exceptions
    def general_districts(self):
        return self.service.get_districts()
    
    @handle_logs_and_exceptions
    def general_shipping_types(self):
        return self.service.get_shipping_types()