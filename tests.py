import json
import sqlite3
import unittest

from concurrent.futures import ThreadPoolExecutor

from virtualMachineAdmin import VirtualMachineAdmin


def setup_database(connection):
    cursor = connection.cursor()
    cursor.execute("""drop table if exists vm_reservations""")
    cursor.execute(
        """create table if not exists vm_reservations (`vm_id` varchar(40) not null, `ip_address` varchar(30) ,
         `vm_status` varchar(20) , primary key(vm_id)) """)
    connection.commit()
    cursor.close()


class TestVirtualMachineAdmin(unittest.TestCase):
    """
    Test the add function from the mymath library
    """
    print("Executing the unit tests for the methods of VirtualMachineAdmin Class")
    def setUp(self):
        self.conn = sqlite3.connect("vm_db")
        setup_database(self.conn)
        self.vmAdmin = VirtualMachineAdmin(35, sqlite3.connect("vm_db"))
        print(self._testMethodName, ' : test case setup Done')

    def test_multiple_concurrent_checkout(self):
        """
        Test case to concurrently checkout multiple VMs in parallel and make sure no two threads checkout same VM.
        :return: None
        """
        print("Testing checking-out multiple VMs at once.")
        print("*******************************************")
        thread_count = 8
        cursor = self.conn.cursor()
        create_pool = ThreadPoolExecutor(max_workers=thread_count)
        for _ in range(thread_count):
            create_pool.submit(self.vmAdmin.create_vm())

        sql = "SELECT vm_id FROM vm_reservations where vm_status = 'available' "
        cursor.execute(sql)
        available_vm_beforecheckout = cursor.fetchall()
        # available_vm_beforecheckout will be list of vm_ids of VMs that are in the available state.

        checkout_pool = ThreadPoolExecutor(max_workers=len(available_vm_beforecheckout))
        for _ in range(thread_count):
            checkout_pool.submit(self.vmAdmin.checkout_vm())

        sql = "SELECT vm_id FROM vm_reservations where vm_status = 'checked-out' "
        cursor.execute(sql)
        checkedout_vms = cursor.fetchall()
        #   checkedout_vms will be the list of vm_ids of VMs that are checked-out

        #   if atleast one VM is checked out by two processes at once, then the difference between
        # count of available_vm_beforecheckout and count of checkedout_vms will not be equal
        print("*******************************************")
        cursor.close()
        self.assertEqual(len(available_vm_beforecheckout), len(checkedout_vms))

    def test_create_1(self):
        """
        Test Case to check the successful VM Creation
        """
        result = self.vmAdmin.create_vm()  # Creating VM
        result = json.loads(result)
        self.assertEqual('success', result['status'])

    def test_create_2(self):
        """
        Test Case to check the if VM Created is in available/error state in return message or not.
        """
        result = self.vmAdmin.create_vm()  # Creating VM
        result = json.loads(result)
        print("VM State: ", result['data']['vm_status'])
        self.assertIn(result['data']['vm_status'], ['available', 'error'])

    def test_checkout_1(self):
        """
        Test case to check if vm can be checkedout successfully or not
        """
        create_result = self.vmAdmin.create_vm()  # Creating VM
        create_result = json.loads(create_result)
        # Making sure that the VM created is not in 'error' state
        while create_result['data']['vm_status'] != 'available':
            create_result = self.vmAdmin.create_vm()
            create_result = json.loads(create_result)

        result = self.vmAdmin.checkout_vm()  # Checkout-vm
        result = json.loads(result)

        self.assertEqual('success', result['status'])

    def test_checkout_2(self):
        """
        Test case to see if vm checked-out has the checked-out state in the return message
        """
        create_result = self.vmAdmin.create_vm()  # Creating VM
        create_result = json.loads(create_result)
        # Making sure that the VM created is not in 'error' state
        while create_result['data']['vm_status'] != 'available':
            create_result = self.vmAdmin.create_vm()
            create_result = json.loads(create_result)

        result = self.vmAdmin.checkout_vm()  # Checkout VM
        result = json.loads(result)
        self.assertEqual('checked-out', result['data']['vm_status'])

    def test_get_1(self):
        """
        Test case to check if requested vm is obtained or not
        """
        create_result = self.vmAdmin.create_vm()  # Create VM
        create_result_json = json.loads(create_result)
        result = self.vmAdmin.get_vm(create_result_json['data']['vm_id'])  # Get vm
        result = json.loads(result)
        self.assertDictEqual(create_result_json, result)

    def test_get_2(self):
        """
        Test case to check if correct message is displayed for wrong vm_id
        """
        result = self.vmAdmin.get_vm('dummy-value')  # Getting VM
        self.assertIn('Could not find a vm with given unique ID', result)

    def test_get_status_1(self):
        """
        Test case to check if the correct vm_status is obtained.
        """
        create_result = self.vmAdmin.create_vm()  # Creating VM
        create_result_json = json.loads(create_result)
        result = self.vmAdmin.get_vm_status(
            create_result_json['data']['vm_id'])  # Get VM Status with created vm details
        result = json.loads(result)
        self.assertEqual(create_result_json['data']['vm_status'], result['data']['vm_status'])

    def test_get_status_2(self):
        """
        Test case to check if correct message is displayed for wrong vm_id
        """
        result = self.vmAdmin.get_vm_status('dummy-value')  # Get vm details with wrong vm_id
        result = json.loads(result)
        self.assertEqual('Could not find a vm with given unique ID', result['message'])

    def test_checkin_1(self):
        """
        Test case to check-in a VM
        """
        create_result = self.vmAdmin.create_vm()  # Creating VM
        create_result = json.loads(create_result)
        # Making sure that the VM created is not in 'error' state
        while create_result['data']['vm_status'] != 'available':
            create_result = self.vmAdmin.create_vm()
            create_result = json.loads(create_result)

        checkout_result = self.vmAdmin.checkout_vm()  # Checkout VM
        checkout_result = json.loads(checkout_result)
        #  Checkin in VM with the same details as the checked-out VM
        checkin_result = self.vmAdmin.checkin_vm(checkout_result['data']['vm_id'], checkout_result['data']['ip'])
        checkin_result = json.loads(checkin_result)
        self.assertDictEqual(create_result, checkin_result)

    def test_checkin_2(self):
        """
        Test case to check if correct message is displayed for wrong vm_id
        """
        result = self.vmAdmin.checkin_vm('dummy-id', 'dummy-ip')  # Checkin in vm with wrong vm_id
        result = json.loads(result)
        self.assertIn('Could not find a vm with given details', result['message'])

    def test_checkin_3(self):
        """
        Test case for checkin-in a vm thats not in checked-out state.
        """
        create_result = self.vmAdmin.create_vm()  # Create VM
        create_result = json.loads(create_result)
        # Checking in vm with the information of a vm thats in 'available' state.
        checkin_result = self.vmAdmin.checkin_vm(create_result['data']['vm_id'], create_result['data']['ip'])
        checkin_result = json.loads(checkin_result)
        self.assertEqual("You cannot check-in a VM that is in ' {0} ' State".format(create_result['data']['vm_status']),
                         checkin_result['message'])

    def tearDown(self):
        print(self._testMethodName, ' : test case tear down')
        self.conn.close()


if __name__ == '__main__':
    unittest.main()

