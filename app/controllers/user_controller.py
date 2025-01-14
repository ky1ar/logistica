import logging

from app.services.user_service import UserService
from app.services.utils_service import handle_logs_and_exceptions

class UserController:
    def __init__(self):
        self.service = UserService()     


    @handle_logs_and_exceptions
    def user_get_by_document(self, document):
        if not document:
            return 'Missing document', 400
        
        return self.service.get_user_by_document(document)
    