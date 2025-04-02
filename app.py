from flask import Flask, request, render_template, redirect, url_for, abort
import os
import string
import random
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from config import Config
import re

app = Flask(__name__)
app.config.from_object(Config)

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/minitex.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Minitex startup')

def generate_id(length=5):
    """生成随机记事本ID"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_note_path(note_id):
    """获取记事本文件路径"""
    if not re.match(r'^[a-z0-9]+$', note_id):
        abort(400)
    return os.path.join(app.config['DATA_DIR'], note_id + '.txt')

def cleanup_old_notes():
    """清理过期笔记"""
    try:
        cutoff_date = datetime.now() - timedelta(days=app.config['NOTE_LIFETIME_DAYS'])
        for filename in os.listdir(app.config['DATA_DIR']):
            filepath = os.path.join(app.config['DATA_DIR'], filename)
            if os.path.getmtime(filepath) < cutoff_date.timestamp():
                os.remove(filepath)
                app.logger.info(f'Deleted old note: {filename}')
    except Exception as e:
        app.logger.error(f'Error during cleanup: {str(e)}')

@app.before_request
def before_request():
    """请求预处理"""
    pass  # 移除HTTPS检查

@app.route('/')
def index():
    """主页 - 创建新记事本"""
    try:
        note_id = generate_id(app.config['NOTE_ID_LENGTH'])
        while os.path.exists(get_note_path(note_id)):
            note_id = generate_id(app.config['NOTE_ID_LENGTH'])
        os.makedirs(app.config['DATA_DIR'], exist_ok=True)
        return redirect(url_for('note', note_id=note_id))
    except Exception as e:
        app.logger.error(f'Error creating new note: {str(e)}')
        abort(500)

@app.route('/<note_id>')
def note(note_id):
    """显示记事本页面"""
    try:
        note_path = get_note_path(note_id)
        content = ''
        if os.path.exists(note_path):
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return render_template('note.html', content=content)
    except Exception as e:
        app.logger.error(f'Error accessing note {note_id}: {str(e)}')
        abort(500)

@app.route('/<note_id>', methods=['POST'])
def save_note(note_id):
    """保存记事本内容"""
    try:
        content = request.form.get('content', '')
        if len(content.encode('utf-8')) > app.config['MAX_NOTE_SIZE']:
            abort(413)  # 内容过大
        
        note_path = get_note_path(note_id)
        os.makedirs(app.config['DATA_DIR'], exist_ok=True)
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        cleanup_old_notes()  # 清理旧笔记
        return 'OK'
    except Exception as e:
        app.logger.error(f'Error saving note {note_id}: {str(e)}')
        abort(500)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='页面未找到'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='服务器内部错误'), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('error.html', error='内容超出大小限制'), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)