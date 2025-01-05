from app import db

class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            result[column.name] = value
        return result


class Users(BaseModel):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    levels = db.Column(db.Integer)
    document = db.Column(db.String(255)) #unique=True
    name = db.Column(db.String(255))
    nick = db.Column(db.String(255))
    role = db.Column(db.String(255))
    image = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    stamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
