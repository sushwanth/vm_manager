from DBConnecton import  DBConnector

dbcon = DBConnector('localhost', 3306, 'root', 'password')

dbcon.select_query('select * from vm_db.vm_reservations')

dbcon.update_query('update vm_db.vm_reservations set vm_status = "test" where ip_address = "rr3" ')

dbcon.close()






# import asyncio
# import asyncio
# import requests
#
# async def main():
#     loop = asyncio.get_event_loop()
#     futures = [
#         loop.run_in_executor(
#             None,
#             requests.get,
#             'http://127.0.0.1:5000/checkoutVM/'
#         )
#         for i in range(8)
#     ]
#     for response in await asyncio.gather(*futures):
#         pass
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
#
