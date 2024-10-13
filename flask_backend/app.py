from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
from helper import chat_with_llm, combine_files_to_string
from cap import plot_market_cap_distribution
from graph import plot_industry_performance
from insight import save_industry_analysis
from news import save_industry_news

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

link_map = {}

@app.route('/')
def home():
    return jsonify({ "message": "API is running!" }), 200

@app.route('/login')
def login():
    session_id = str(uuid.uuid4())
    return jsonify({ "session_id": session_id }), 200

@app.route('/generate_doc', methods=['POST'])
def generate_doc():
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    
    session_id = request.json['session_id']
    industry = request.json['industry']
    brief = request.json['brief']
    
    directory_path = os.path.join(app.config['UPLOAD_FOLDER'], str(session_id))
    os.makedirs(directory_path, exist_ok=True)
    
    plot_market_cap_distribution(directory_path, industry) # market_cap_distribution.jpg
    plot_industry_performance(directory_path, industry) # performance_graph.jpg
    save_industry_analysis(directory_path, industry, brief) # insights.md, data.md
    save_industry_news(directory_path, industry) # news.md
    
    # TODO: make google doc
    google_doc_link = 'docs.google.com/abc123'
        
    link_map[session_id] = google_doc_link
    return jsonify({ "link": google_doc_link }), 201

@app.route('/previous_session', methods=['POST'])
def previous_session():
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    
    session_id = request.json['session_id']
    if session_id not in link_map:
        return jsonify({"error": "Session ID not found!"}), 400
    
    return jsonify({ "message": f"Session ID ({session_id}) found!", "link": link_map[session_id] }), 201

@app.route('/follow-up', methods=['POST'])
def follow_up():
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    
    query = request.json['prompt']
    session_id = request.json['session_id']
    
    directory_path = os.path.join(app.config['UPLOAD_FOLDER'], str(session_id))
    file_content = combine_files_to_string(directory_path)
    
    llm_response = chat_with_llm(file_content + '\n\n' + query)
    if llm_response == '':
        return jsonify({"error": "No response from LLM!"}), 400
    
    return jsonify({ "message": f"{llm_response}" }), 201
    

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
