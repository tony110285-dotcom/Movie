from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# 數據文件路徑
DATA_FILE = 'movies_data.json'

# 初始化數據
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'movies': [
            {
                'id': 1,
                'title': '奪冠',
                'description': '中國女排的故事',
                'date': '2026-03-15',
                'time': '19:00',
                'location': '電影院1號廳',
                'capacity': 50,
                'image': 'https://via.placeholder.com/300x400?text=Movie1'
            },
            {
                'id': 2,
                'title': '滅絕',
                'description': '科幻冒險之旅',
                'date': '2026-03-22',
                'time': '20:00',
                'location': '電影院2號廳',
                'capacity': 40,
                'image': 'https://via.placeholder.com/300x400?text=Movie2'
            }
        ],
        'registrations': []
    }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/movies', methods=['GET'])
def get_movies():
    data = load_data()
    return jsonify(data['movies'])

@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    data = load_data()
    movie = next((m for m in data['movies'] if m['id'] == movie_id), None)
    if movie:
        # 計算已報名人數
        registrations = [r for r in data['registrations'] if r['movie_id'] == movie_id]
        movie['registered'] = len(registrations)
        return jsonify(movie)
    return jsonify({'error': '電影未找到'}), 404

@app.route('/api/register', methods=['POST'])
def register():
    data = load_data()
    registration = request.json
    
    # 驗證數據
    if not registration.get('name') or not registration.get('movie_id'):
        return jsonify({'error': '缺少必要信息'}), 400
    
    movie = next((m for m in data['movies'] if m['id'] == registration['movie_id']), None)
    if not movie:
        return jsonify({'error': '電影未找到'}), 404
    
    # 檢查是否已滿座
    registrations = [r for r in data['registrations'] if r['movie_id'] == registration['movie_id']]
    if len(registrations) >= movie['capacity']:
        return jsonify({'error': '報名已滿'}), 400
    
    # 添加報名記錄
    registration['id'] = len(data['registrations']) + 1
    registration['timestamp'] = datetime.now().isoformat()
    data['registrations'].append(registration)
    save_data(data)
    
    return jsonify({'success': True, 'id': registration['id']})

@app.route('/api/registrations/<int:movie_id>', methods=['GET'])
def get_registrations(movie_id):
    data = load_data()
    registrations = [r for r in data['registrations'] if r['movie_id'] == movie_id]
    return jsonify(registrations)

if __name__ == '__main__':
    app.run(debug=True, port=5000)