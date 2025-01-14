import time
from Config import *
import Services.lora as lora
from flask import Flask, render_template, jsonify, jsonify
from threading import Thread
import re
@app.route('/')
def control_panel():
    return render_template('control_panel.html')

@app.route('/random_cmd')
def random_cmd():
    # Trigger deployment of the payload
    # Sending an RF signa
    lora.send_random()
    return "Hello from server"

@app.route('/command/<command>')
def send_command(command = ""):
    print("Executing command", command)
    if lora.arduino == None:
        return jsonify(message="Serial not started"), 400
    try:
        lora.serial_input(command)
        return jsonify(message="Command sent"), 200
    except Exception as e:
        print(f'Exception {e}')
        return jsonify(message = "Server error: {e}"), 500

@app.route('/serial_start/<port>')
def start_serial(port = "COM7"):
    try:
        lora.connect(port)
        print(f'Stablishing serial {port}')
        lora_telem_thread = Thread(target=lora.receive_data)
        lora_telem_thread.daemon = True
        lora_telem_thread.start()
        return jsonify(message = "Started Serial"), 200
    except Exception as e:
        print(f'Error connecting to serial: {e}')
        return jsonify(message = f'Error: {e}'), 500

@app.route('/serial_input/<message>')
def serial_input(message):
    try:
        lora.serial_input(message)
        return jsonify(message = "OK"), 200
    except Exception as e:
        print(f'Exception with Serial Input')
        return jsonify(message=f'Error {e}'),500

def log_lora(message):
    socketio.emit('lora_log', {'message':message})

def log_serial(message):
    socketio.emit('serial_log', {'message', message})

@app.route('/close_serial')
def close_serial():
    try:
        lora.close()
    except Exception as e:
        msg = f"Unable to Close Serial Connection: {e}"
        print(msg)
        return jsonify(message = msg), 500
    return jsonify(message='OK'),200

# SENDER FUNCTIONS
def update_alti(alti):
    socketio.emit('alti_update',{'alti':alti})

def log_msg(message):
    socketio.emit('alti_log', {'message':message})