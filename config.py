import os

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    DATA_DIR = 'data'
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 限制请求大小为1MB
    
    # 安全配置
    NOTE_ID_LENGTH = 5
    MAX_NOTE_SIZE = 500 * 1024  # 500KB
    NOTE_LIFETIME_DAYS = 30  # 笔记保存天数