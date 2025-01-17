from application import db

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


class ShippingTypes(BaseModel):
    __tablename__ = 'shipping_types'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100))

class ShippingStatus(BaseModel):
    __tablename__ = 'shipping_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class ShippingSchedule(BaseModel):
    __tablename__ = 'shipping_schedule'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class Drivers(BaseModel):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255))
    hex_color = db.Column(db.String(7))


class Districts(BaseModel):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255))


class PurchaseOrders(BaseModel):
    __tablename__ = 'purchase_orders'

    number = db.Column(db.String(100), primary_key=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    shipping_type_id = db.Column(db.Integer, db.ForeignKey('shipping_types.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    creation_date = db.Column(db.DATE, nullable=False)
    #insert_stamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    comments = db.Column(db.String(255))
    shipping_status_id = db.Column(db.Integer, db.ForeignKey('shipping_status.id'), nullable=False)
    shipping_date = db.Column(db.DATE, nullable=False)
    shipping_schedule_id = db.Column(db.Integer, db.ForeignKey('shipping_schedule.id'))
    
    client = db.relationship("Users", lazy="joined", foreign_keys=[client_id])
    admin = db.relationship("Users", lazy="joined", foreign_keys=[admin_id])
    district = db.relationship("Districts", lazy="joined", foreign_keys=[district_id])
    driver = db.relationship("Drivers", lazy="joined", foreign_keys=[driver_id])
    shipping_type = db.relationship("ShippingTypes", lazy="joined", foreign_keys=[shipping_type_id])
    shipping_status = db.relationship("ShippingStatus", lazy="joined", foreign_keys=[shipping_status_id])
    shipping_schedule = db.relationship("ShippingSchedule", lazy="joined", foreign_keys=[shipping_schedule_id])




