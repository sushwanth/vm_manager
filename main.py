from virtualMachineAdmin import virtualMachineAdmin

vmAdmin = virtualMachineAdmin(40)

for i in range(5):
    vm = vmAdmin.create_vm()

# print(vm)
#
# vmAdmin.print_vm()
#
#
# for i in range(5):
#     vmAdmin.checkout_vm()
#
# for i in range(5):
#     vm = vmAdmin.checkout_vm()
#     print(vm)
#
# vm = vmAdmin.checkout_vm()
# print(vm)


# CREATE DATABASE IF NOT EXISTS vm_table;
# create table if not exists `vm_table`.`vm_reservation`
#               (`unique_id` varchar(30) not null, `ip_address` varchar(30) , `status` varchar(20) ,
#               `vm_name` varchar(30), primary key(unique_id));

# import pymysql
#
# dbc = ("localhost", "root", "password", "vm_table")
#
# import pymysql
#
# import mysql.connector
#
# conn = mysql.connector.Connect(host='localhost', port=3306, user='root', passwd='password', db='vm_table')
#
# cur = conn.cursor()
#
# cur.execute("""INSERT INTO vm_reservation VALUES (%s,%s,%s, %s)""",('uuid1',"132.123.12.12",'in-use', "name" ))
# conn.commit()






# for key in self.dict_:
        #     if self.dict_[key]['vm_status'] == 'available':
        #         selected_vm = key
        #         self.dict_[key]['vm_status'] = 'in-use'
        #         break
        #     if self.dict_[key]['vm_status'] == 'creating-available':
        #         selected_vm = key
        #         self.dict_[key]['vm_status'] = 'creating-assigned'
        #         break
        # if selected_vm is None:
        #     created_vm = json.loads(self.create_vm())
        #     if created_vm['vm_status'].find('Error') != -1:
        #         created_vm[
        #             'vm_status'] = "Error: No VM is available and maximum VM Count reached, please try after some time"
        #         return json.dumps(created_vm)
        #
        #     selected_vm = created_vm['unique_id']
        #     self.dict_[selected_vm]['vm_status'] = 'creating-assigned'
