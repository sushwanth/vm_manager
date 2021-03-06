import mysql.connector
from flask import Flask, json, request

from virtualMachineAdmin import VirtualMachineAdmin

vmAdmin = VirtualMachineAdmin(30, mysql.connector.Connect(host='db', port=3306, user='root', password='password',
                                                          database='vm_db'))

app = Flask(__name__)


@app.route("/")
def index():
    return json.dumps({'data': None, 'message': 'You have reached the index page'})  # jsonStr


@app.route("/createVM/")
def create_vm():
    try:
        response = vmAdmin.create_vm()  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


@app.route("/deleteVM/")
def delete_vm():
    try:
        unique_id = request.args.get('unique_id')
        ip = request.args.get('ip')
        response = vmAdmin.delete_vm(unique_id, ip)  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


@app.route("/getVMStatus/")
def get_vm_status():
    try:
        unique_id = request.args.get('unique_id')
        response = vmAdmin.get_vm_status(unique_id)  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


@app.route("/getVM/")
def get_vm():
    try:
        unique_id = request.args.get('unique_id')
        response = vmAdmin.get_vm(unique_id)  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


@app.route("/checkoutVM/")
def checkout_vm():
    try:
        response = vmAdmin.checkout_vm()  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


@app.route("/checkinVM/")
def checkin_vm():
    try:
        unique_id = request.args.get('unique_id')
        ip = request.args.get('ip')
        response = vmAdmin.checkin_vm(unique_id, ip)  # jsonStr
    except Exception as e:
        error_message = str(e)
        response = {'status': 'error',
                    'data': None,
                    'message': error_message}
    finally:
        return json.dumps(response)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
