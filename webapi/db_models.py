from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

__all__ = ('db',
           'Account',
           'Location',
           'VisitedLocation',
           'AnimalType',
           'Animal',
           )

db = SQLAlchemy()


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)


class VisitedLocation(db.Model):
    __tablename__ = 'visited_locations'

    id = db.Column(db.Integer, primary_key=True)
    visit_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    location_id = db.Column(db.Integer, nullable=False)


class AnimalType(db.Model):
    __tablename__ = 'animal_types'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)


class Animal(db.Model):
    __tablename__ = 'animals'

    id = db.Column(db.Integer, primary_key=True)
    animal_types = db.Column(ARRAY(db.Integer), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String, nullable=False)
    life_status = db.Column(db.String, nullable=False, default='ALIVE')
    chipping_datetime = db.Column(db.DateTime(timezone=True), nullable=False)
    chipper_id = db.Column(db.Integer, nullable=False)
    chipping_location_id = db.Column(db.Integer, nullable=False)
    visited_locations = db.Column(ARRAY(db.Integer), default=[])
    death_datetime = db.Column(db.DateTime(timezone=True), default=None)
