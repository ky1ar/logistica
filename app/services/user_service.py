import logging

from datetime import datetime, timezone, timedelta
from app.models.models import Users
from app.services.utils_service import handle_exceptions, handle_db_exceptions
from flask import g


class UserService:

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
    