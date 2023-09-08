import logging

# logging.basicConfig(
#     format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
#     level=logging.INFO,
# # level=
#     )

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d.%m.%y %H:%M:%S',
    level=logging.INFO
    )
