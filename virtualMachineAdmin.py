import json
import threading
from time import sleep
import uuid
from random import randrange
import mysql.connector


class VirtualMachineAdmin(object):

    _vms_created = 0

    def __init__(self, max_vm_count):
        """
        :param max_vm_count: The maximum number of VMs that can be created.
        """
        self._max_vm_count = max_vm_count
        self.conn = mysql.connector.Connect(host='db', port=3306, user='root', password='password')
        self.cursor = self.conn.cursor(buffered=True)
        create_db_command = "CREATE DATABASE IF NOT EXISTS vm_db"
        create_table_command = "create table if not exists vm_db.vm_reservations (`vm_id` varchar(40) not null, `ip_address` varchar(30) , `vm_status` varchar(20) , primary key(vm_id)) "
        self.cursor.execute(create_db_command)
        self.cursor.execute(create_table_command)
        self.cursor.execute("select * from vm_db.vm_reservations ")
        self._used_ips = [self.cursor.fetchall()][0]
        self._vms_created = len(self._used_ip)

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

    def update_vm(self, vm_id, vm_status):
        """
        Method to update the status of the VM once its creation is completed.
        This method has been created to simulate the time taken for a vm creation.
        :param vm_id: the unique_id of the VM.
        :param vm_status: status to be updated.
        :return: None
        """
        sleep_time = 10
        print("Time taken for creating the VM: ", sleep_time)
        for i in range(0, sleep_time+1, 5):
            print('Seconds elapsed: ', i, ' to create the VM: ', vm_id)
            sleep(5)

        cmd = "update vm_db.vm_reservations set vm_status = \"%s\"  where vm_id = \"%s\" " % (vm_status, vm_id)
        self.cursor.execute(cmd)
        self.conn.commit()
        print("The VM: ", vm_id, "has been created and is available")

    def create_vm(self):
        """
        Method to create a new VM.
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            # Checking if the total number of VMs has exceeded the specified count or not.
            if self._vms_created >= self._max_vm_count:
                print("Maximum VMs has already been created. Cannot create anymore VMs.")
                return json.dumps({'status': 'error',
                                   'data': None,
                                   'message': 'Error: Maximum VM Count reached'})
            # Incrementing the count of the VMs created.
            self._vms_created += 1
            print('Generating vm_id and ip')
            vm_id = str(uuid.uuid4())  # Generating an unique ID for the VM.
            ip = self.generate_ip()  # Generating a random IP for the VM.
            self.cursor.execute("select * from vm_db.vm_reservations where ip_address like '%s'" % ip)
            result = self.cursor.fetchall()

            # Checking if the IP address has already been used for any of the VMs.
            print("Checking if the IP address has already been used for any of the VMs: ", self._used_ips)
            while ip in self._used_ips:
                print("IP Exists, re-generating it")
                ip = self.generate_ip()

            self._used_ips.append(ip)

            res = "insert into vm_db.vm_reservations (vm_id,ip_address,vm_status) values (\"%s\",\"%s\",\"%s\")" % (
                vm_id, ip, 'creating')
            self.cursor.execute(res)
            self.conn.commit()

            print("Creating the VM: ", vm_id, " and assigning the IP: ", ip)
            # Introducing sleep time to simulate the time for creating the VM.
            update_vm_thread = threading.Thread(target=self.update_vm, args=(vm_id,'available',))
            update_vm_thread.daemon = True      # Setting Daemon = True for the thread to run in the background.
            update_vm_thread.start()            # This would be the thread to create the VM, it runs in the background.

            print("Created the VM:", vm_id, ip)

            return_json = {'status': 'success',
                           'data': {'vm_id': vm_id,
                                    'ip': ip,
                                    'vm_status': 'creating'},
                           'message': None}

        except Exception as e:
            error_message = "Error " + str(e) + "while creating the VM: " + str(vm_id)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message}
            self.conn.rollback()
            self.cursor.close()
            self.cursor = self.conn.cursor(buffered=True)

        finally:
            return json.dumps(return_json)

    def delete_vm(self, vm_id, ip):
        """
        Method to delete the VM which is not being used or created, using the vm_id and ip.
        :param vm_id: unique id of the vm to be deleted
        :param ip: ip address of the vm to be deleted
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            error_message = 'No VM exists with the given vm_id and ip'
            cmd = "select * from vm_db.vm_reservations where vm_id = \"%s\" and ip_address = \"%s\" " % (
                vm_id, ip)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()
            if result:
                selected_vm = result[0][0]
                ip = result[1]
                if result[-1] == 'available':
                    cmd = "delete from vm_db.vm_reservations where ip_address = \"%s\" and vm_id = \"%s\" " % (
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
                    error_message = "You cannot delete a VM that is in ' %s ' State" % (result[-1])
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
            self.cursor = self.conn.cursor(buffered=True)

        finally:
            return json.dumps(return_json)

    def get_vm(self, vm_id):
        """
        Method to get the VM details using the vm_id 
        :param vm_id: The vm_id of the VM whose information is to be returned.
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            cmd = "select * from vm_db.vm_reservations where vm_id like '%s'" % vm_id
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
            self.cursor = self.conn.cursor(buffered=True)

        finally:
            return json.dumps(return_json)

    def get_vm_status(self, vm_id):
        """
        Get the status of the VM using it vm_id. 
        :param vm_id: The vm_id of the VM whose information is to be returned.
        :return: A json response object status of the VM.
        """
        try:
            cmd = "select vm_status from vm_db.vm_reservations where vm_id like \"%s\"" % vm_id
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
            self.cursor = self.conn.cursor(buffered=True)

        finally:
            return json.dumps(return_json)

    def checkout_vm(self):
        """ 
        Method to checkout an available VM. 
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            get_available_vm_cmd = "select * from vm_db.vm_reservations where vm_status like 'available' limit 1 "
            self.cursor.execute(get_available_vm_cmd)
            result = self.cursor.fetchall()
        except Exception as e:
            error_message = "Error while finding available VMs: " + str(e)
            return_json = {'status': 'error',
                           'data': None,
                           'message': error_message }

            self.cursor.close()
            self.cursor = self.conn.cursor(buffered=True)

        try:
            if result:
                selected_vm = result[0][0]
                update_vm_status_cmd = "update vm_db.vm_reservations set vm_status = \"checked-out\" where vm_id = \"%s\"" % (
                    selected_vm)
                self.cursor.execute(update_vm_status_cmd)
                self.conn.commit()
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
            self.cursor = self.conn.cursor(buffered=True)
        finally:
            return json.dumps(return_json)

    def checkin_vm(self, vm_id, ip):
        """
        Method to check-in the VM by giving the vm_id and the ip of the VM.
        :param vm_id: unique id of the VM. 
        :param ip:ip address of the VM. 
        :return: A json response object with vm_id, ip_address and status
        """
        try:
            error_message = 'No VM exists with the given vm_id and ip'
            cmd = "select * from vm_db.vm_reservations where vm_id like \"%s\" and ip_address like \"%s\" " % (
                vm_id, ip)
            self.cursor.execute(cmd)
            result = self.cursor.fetchall()
            if result:
                selected_vm = result[0][0]
                if result[-1] == 'checked-out':
                    cmd = "update vm_db.vm_reservations set vm_status = \"available\" where vm_id = \"%s\" " % (
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
                    error_message = "You cannot check-in a VM that is in ' %s ' State" % (result[-1])
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
            self.cursor = self.conn.cursor(buffered=True)
        finally:
            return json.dumps(return_json)