"""
Configuration - Live Demo
Repository: https://github.com/willialso/atticusPro_liveDemo
"""
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'atticus-live-demo-key'
    DEBUG = True
    REPOSITORY_URL = 'https://github.com/willialso/atticusPro_liveDemo'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
