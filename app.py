"""Flask server for browser-based agent visualization and control."""
import json
import threading
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for

from events import RunLogger


def create_app(run_dir: Path, gate_event: threading.Event):
    """Create Flask app with shared state."""
    app = Flask(__name__)
    
    # Shared state
    app.run_dir = run_dir
    app.gate_event = gate_event
    app.logger = RunLogger(run_dir)
    
    @app.route('/')
    def index():
        """Redirect to current run."""
        return redirect(url_for('run_view', run_id=run_dir.name))
    
    @app.route('/run/<run_id>')
    def run_view(run_id):
        """Display run visualization page."""
        return render_template('run.html', run_id=run_id)
    
    @app.route('/run/<run_id>/events')
    def get_events(run_id):
        """Get all events for a run."""
        # Read events from the JSONL file
        events_file = Path("runs") / run_id / "events.jsonl"
        events = []
        
        if events_file.exists():
            with open(events_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        
        return jsonify(events)
    
    @app.route('/run/<run_id>/next', methods=['POST'])
    def next_step(run_id):
        """Trigger next step by setting the gate event."""
        if hasattr(app, 'gate_event'):
            app.gate_event.set()
        return '', 204
    
    return app


if __name__ == '__main__':
    # For testing - create a dummy run and event
    from datetime import datetime
    
    run_dir = Path("runs") / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    gate_event = threading.Event()
    
    app = create_app(run_dir, gate_event)
    app.run(debug=True, port=5000)