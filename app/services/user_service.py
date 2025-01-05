import logging

from app.models.models import Users
from app.services.utils_service import handle_exceptions, handle_db_exceptions
from flask import g


class UserService:

    @handle_db_exceptions
    def get_user_by_document(self, document):
        user = g.db_session.query(Users).filter_by(document=document).first()
        if not user:
            return 'User not found', 400
        
        return user.to_dict(), 200
