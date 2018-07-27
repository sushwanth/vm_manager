import json
import threading
import uuid

from random import randrange, choice
from time import sleep


class VirtualMachineAdmin(object):

    def __init__(self, max_vm_count, connection):
        """
        :param max_vm_count: The maximum number of VMs that can be created.
        """
        self._max_vm_count = max_vm_count
        self._checkin_thread = threading.Lock()
        self._checkout_thread = threading.Lock()
        self._create_thread = threading.Lock()
        self._delete_thread = threading.Lock()
        self.conn = connection
        self.cursor = self.conn.cursor()
        self.cursor.execute("select ip_address from vm_reservations ")
        self._used_ips = [self.cursor.fetchall()][0]
        self._vm_count = len(self._used_ips)

    @staticmethod
    def generate_ip():
        """
        Method to generate a random IP address.
        :return: ip address as a string.
        """
        # Following IPs are excluded as they are to be used as private ips.
        excluded_ips = [10, 172, 192]
        ip_part_one = randrange(1, 256)
        while ip_part_one in excluded_ips:
            ip_part_one = randrange(1, 256)
        ip = '.'.join([str(ip_part_one), str(randrange(1, 256)), str(randrange(1, 256)), str(randrange(1, 256))])
        print('IP Generated: ', ip)
        return ip

    def create_vm(self):
        """
        Method to create a new VM.
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            self._create_thread.acquire()
            # Checking if the total number of VMs has exceeded the specified count or not.
            if self._vm_count >= self._max_vm_count:
                print("Maximum VMs has already been created. Cannot create anymore VMs.")
                return_json = {'status': 'error',
                               'data': None,
                               'message': 'Error: Maximum VM Count reached'}
                return
            # Incrementing the count of the VMs created.
            self._vm_count += 1
            print('Generating vm_id and ip')
            vm_id = str(uuid.uuid4())  # Generating an unique ID for the VM.
            ip = self.generate_ip()  # Generating a random IP for the VM.
            # Checking if the IP address has already been used for any of the VMs.
            print("Checking if the IP address has already been used for any of the VMs ")
            self.cursor.execute("select ip_address from vm_reservations where ip_address = \"{0}\"".format(ip))
            used_ips = self.cursor.fetchall()
            while used_ips != []:  # if used_ips == [] it means that the ip generated is not being used by any other VM.
                print("IP Exists, re-generating it")
                ip = self.generate_ip()
                self.cursor.execute("select ip_address from vm_reservations where ip_address = \"{0}\"".format(ip))
                used_ips = self.cursor.fetchall()

            sleep(5)  # Introducing sleep time to simulate the time for creating the VM.
            vm_status = choice(['available','error'])
            res = "insert into vm_reservations (vm_id,ip_address,vm_status) values (\"{0}\",\"{1}\",\"{2}\")".format(
                vm_id, ip, vm_status)
            self.cursor.execute(res)
            self.conn.commit()

            print("Creating the VM: ", vm_id, " and assigning the IP: ", ip)

            return_json = {'status': 'success',
                           'data': {'vm_id': vm_id,
                                    'ip': ip,
                                    'vm_status': vm_status},
                           'message': None}
        except Exception as e:
            error_message = "Error " + str(e) + "while creating the VM: " + str(vm_id)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()

        finally:
            self._create_thread.release()
            return json.dumps(return_json)

    def delete_vm(self, vm_id, ip):
        """
        Method to delete the VM which is not being used or created, using the vm_id and ip.
        :param vm_id: unique id of the vm to be deleted
        :param ip: ip address of the vm to be deleted
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            self._delete_thread.acquire()
            error_message = 'No VM exists with the given vm_id and ip'
            cmd = "select * from vm_reservations where vm_id = \"{0}\" and ip_address = \"{1}\" ".format(vm_id, ip)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()
            if result:
                selected_vm = result[0][0]
                ip = result[0][1]
                if result[0][-1] == 'available' or result[0][-1] == 'error':
                    cmd = "delete from vm_reservations where ip_address = \"{0}\" and vm_id = \"{1}\" ".format(
                        ip, selected_vm)
                    self.cursor.execute(cmd)
                    self.conn.commit()
                    return_json = {'status': 'success',
                                   'data': {'vm_id': result[0][0],
                                            'ip': result[0][1],
                                            'vm_status': 'deleted'},
                                   'message': None}
                    return json.dumps(return_json)
                else:
                    error_message = "You cannot delete a VM that is in ' {0} ' State".format(result[0][-1])
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}

        except Exception as e:
            error_message = "Error " + str(e) + "while deleting the VM: " + str(vm_id)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()

        finally:
            self._delete_thread.release()
            return json.dumps(return_json)

    def get_vm(self, vm_id):
        """
        Method to get the VM details using the vm_id 
        :param vm_id: The vm_id of the VM whose information is to be returned.
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            cmd = "select * from vm_reservations where vm_id like \"{0}\"".format(vm_id)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()

            if not result:
                return_json = {'status': 'error',
                               'data': None,
                               'message': 'Could not find a vm with given unique ID'}
            else:
                return_json = {'status': 'success',
                               'data': {'vm_id': result[0][0],
                                        'ip': result[0][1],
                                        'vm_status': result[0][2]},
                               'message': None}
        except Exception as e:
            error_message = "Error " + str(e) + "while getting the VM: " + str(vm_id)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()

        finally:
            return json.dumps(return_json)

    def get_vm_status(self, vm_id):
        """
        Get the status of the VM using it vm_id. 
        :param vm_id: The vm_id of the VM whose information is to be returned.
        :return: A json response object status of the VM.
        """
        try:
            cmd = "select vm_status from vm_reservations where vm_id like \"{0}\"".format(vm_id)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()

            if not result:
                return_json = {'status': 'error',
                               'data': None,
                               'message': 'Could not find a vm with given unique ID'}
            else:
                return_json = {'status': 'success',
                               'data': {'vm_status': result[0][0]},
                               'message': None}
        except Exception as e:
            error_message = "Error " + str(e) + "while getting the VM Status: " + str(vm_id)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()

        finally:
            return json.dumps(return_json)

    def checkout_vm(self):
        """ 
        Method to checkout an available VM. 
        :return: A json response object with vm_id, ip_address and status
        """
        return_json = {'status': 'error',
                       'data': None,
                       'message': 'Unknown error'}
        try:
            self._checkout_thread.acquire()
            get_available_vm_cmd = "select * from vm_reservations where vm_status = 'available' limit 1 "
            self.cursor.execute(get_available_vm_cmd)
            result = self.cursor.fetchall()

            if result:
                selected_vm = result[0][0]
                update_vm_status_cmd = "update vm_reservations set vm_status = \"checked-out\" where vm_id = \"{0}\"".format(
                    selected_vm)
                self.cursor.execute(update_vm_status_cmd)
                self.conn.commit()
                print("Checking out the VM: ", selected_vm)
                return_json = {'status': 'success',
                               'data': {'vm_id': result[0][0],
                                        'ip': result[0][1],
                                        'vm_status': 'checked-out'},
                               'message': None}
            else:
                return_json = {'status': 'error',
                               'data': None,
                               'message': 'No VMs currently available, please try after some time'}
        except Exception as e:
            error_message = "Error " + str(e) + ". While checking-out VM: " + str(selected_vm)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()
        finally:
            self._checkout_thread.release()
            return json.dumps(return_json)

    def checkin_vm(self, vm_id, ip):
        """
        Method to check-in the VM by giving the vm_id and the ip of the VM.
        :param vm_id: unique id of the VM. 
        :param ip:ip address of the VM. 
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            self._checkin_thread.acquire()
            error_message = 'No VM exists with the given vm_id and ip'
            cmd = "select * from vm_reservations where vm_id like \"{0}\" and ip_address like \"{1}\" ".format(vm_id,
                                                                                                               ip)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()
            print("Result", result)

            if result:
                selected_vm = result[0][0]
                if result[0][-1] == 'checked-out':
                    cmd = "update vm_reservations set vm_status = \"available\" where vm_id = \"{0}\" ".format(
                        selected_vm)
                    self.cursor.execute(cmd)
                    self.conn.commit()
                    return_json = {'status': 'success',
                                   'data': {'vm_id': result[0][0],
                                            'ip': result[0][1],
                                            'vm_status': 'available'},
                                   'message': None}
                    return json.dumps(return_json)
                else:
                    error_message = "You cannot check-in a VM that is in ' {0} ' State".format(result[0][-1])
            else:
                error_message = 'Could not find a vm with given details ' + vm_id + " " + ip
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
        except Exception as e:
            error_message = "Error " + str(e) + ". While checking-in VM: " + vm_id
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor()
        finally:
            self._checkin_thread.release()
            return json.dumps(return_json)
