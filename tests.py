import sqlite3
import unittest
import json
import os
from concurrent.futures import ThreadPoolExecutor
import time
import threading
from virtualMachineAdmin import VirtualMachineAdmin

def create_database():
    conn = sqlite3.connect("vm_db")
    cursor = conn.cursor()
    cursor.execute("""create table if not exists vm_reservations (`vm_id` varchar(40) not null, `ip_address` varchar(30) , `vm_status` varchar(20) , primary key(vm_id)) """)
    conn.commit()

def select_all():
    """
    Query the database for all rows
    """
    conn = sqlite3.connect("vm_db")
    cursor = conn.cursor()
    sql = "SELECT * FROM vm_reservations "
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def task():
    print(time.time())
    print("Task Executed {}".format(threading.current_thread()))

class TestVirtualMachineAdmin(unittest.TestCase):
    """
    Test the add function from the mymath library
    """


    def setUp(self):
        create_database()
        self.vmAdmin = VirtualMachineAdmin(30, sqlite3.connect("vm_db"))
        #self.addCleanup(os.remove, 'vm_dbt')

    def test_create_1(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = self.vmAdmin.create_vm()
        result = json.loads(result)
        self.assertEqual('success', result['status'])

    def test_create_2(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = self.vmAdmin.create_vm()
        result = json.loads(result)
        self.assertEqual('available', result['data']['vm_status'])

    def test_checkout_1(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        result = self.vmAdmin.checkout_vm()
        result = json.loads(result)
        self.assertEqual('success', result['status'])

    def test_checkout_2(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        result = self.vmAdmin.checkout_vm()
        result = json.loads(result)
        self.assertEqual('checked-out', result['data']['vm_status'])

    def test_get_1(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        create_result_json = json.loads(create_result)
        result = self.vmAdmin.get_vm(create_result_json['data']['vm_id'])
        result = json.loads(result)
        self.assertDictEqual(create_result_json, result)

    def test_get_2(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = self.vmAdmin.get_vm('dummy-value')
        self.assertIn('Could not find a vm with given unique ID', result)

    def test_get_status_1(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        create_result_json = json.loads(create_result)
        result = self.vmAdmin.get_vm_status(create_result_json['data']['vm_id'])
        result = json.loads(result)
        self.assertEqual(create_result_json['data']['vm_status'], result['data']['vm_status'])

    def test_get_status_2(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = self.vmAdmin.get_vm_status('dummy-value')
        result = json.loads(result)
        self.assertEqual('Could not find a vm with given unique ID', result['message'])

    def test_checkin_1(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        create_result = json.loads(create_result)
        checkout_result = self.vmAdmin.checkout_vm()
        checkout_result = json.loads(checkout_result)
        checkin_result = self.vmAdmin.checkin_vm(checkout_result['data']['vm_id'], checkout_result['data']['ip'])
        checkin_result = json.loads(checkin_result)
        self.assertDictEqual(create_result, checkin_result)

    def test_checkin_2(self):
        """
        Test that the addition of two integers returns the correct total
        """
        result = self.vmAdmin.checkin_vm('dummy-id','dummy-ip')
        result = json.loads(result)
        self.assertIn('Could not find a vm with given details', result['message'])

    def test_checkin_3(self):
        """
        Test that the addition of two integers returns the correct total
        """
        create_result = self.vmAdmin.create_vm()
        create_result = json.loads(create_result)
        checkin_result = self.vmAdmin.checkin_vm(create_result['data']['vm_id'], create_result['data']['ip'])
        checkin_result = json.loads(checkin_result)
        self.assertEqual("You cannot check-in a VM that is in ' available ' State", checkin_result['message'])

    def test_n(self):
        print("Testing checking-out multiple VMs at once.")
        print("*******************************************")
        create_result = self.vmAdmin.create_vm()
        create_result = self.vmAdmin.create_vm()

        executor = ThreadPoolExecutor(max_workers=3)
        task1 = executor.submit(self.vmAdmin.checkout_vm())
        task2 = executor.submit(self.vmAdmin.checkout_vm())
        task3 = executor.submit(self.vmAdmin.checkout_vm())
        print(str(task1),str(task2),str(task3))
        print("*******************************************")
    # def tearDown(self):
    #     os.remove('vm_db')


if __name__ == '__main__':
     unittest.main()


#print(select_all())
#os.remove('vm_db')