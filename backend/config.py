import os

class Config:
    SECRET_KEY = 'medicare-hospital-secret-key-2025'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False