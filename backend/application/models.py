from application import db

class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self, exclude_fields=None):
        exclude_fields = set(exclude_fields) if exclude_fields else set()
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                result[column.name] = getattr(self, column.name)
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
    stamp = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class ShippingMethod(BaseModel):
    __tablename__ = 'shipping_method'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100))
    background = db.Column(db.String(7))
    border = db.Column(db.String(7))


class ShippingStatus(BaseModel):
    __tablename__ = 'shipping_status'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class ShippingSchedule(BaseModel):
    __tablename__ = 'shipping_schedule'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(100))


class ShippingDistricts(BaseModel):
    __tablename__ = 'shipping_districts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(255))


class ShippingContact(BaseModel):
    __tablename__ = 'shipping_contact'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('shipping_orders.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

    order = db.relationship("ShippingOrders", lazy="joined", foreign_keys=[order_id])
    client = db.relationship("Users", lazy="joined", foreign_keys=[client_id])


class ShippingOrders(BaseModel):
    __tablename__ = 'shipping_orders'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    order_number = db.Column(db.String(100), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('shipping_method.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('shipping_status.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('shipping_schedule.id'))
    address = db.Column(db.String(255), nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('shipping_districts.id'), nullable=False)
    comments = db.Column(db.String(255))
    maps = db.Column(db.String(255))
    proof_photo = db.Column(db.String(255))
    register_date = db.Column(db.DATE, nullable=False)
    delivery_date = db.Column(db.DATE, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    
    method = db.relationship("ShippingMethod", lazy="joined", foreign_keys=[method_id])
    driver = db.relationship("Users", lazy="joined", foreign_keys=[driver_id])
    vendor = db.relationship("Users", lazy="joined", foreign_keys=[vendor_id])
    admin = db.relationship("Users", lazy="joined", foreign_keys=[admin_id])
    status = db.relationship("ShippingStatus", lazy="joined", foreign_keys=[status_id])
    schedule = db.relationship("ShippingSchedule", lazy="joined", foreign_keys=[schedule_id])
    district = db.relationship("ShippingDistricts", lazy="joined", foreign_keys=[district_id])

    contacts = db.relationship("ShippingContact", lazy="joined", foreign_keys=[ShippingContact.order_id])



