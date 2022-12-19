from dronekit import connect, VehicleMode
from dronekit_sitl import SITL, start_default

sitl = SITL()
sitl.download("plane", "3.3.0", verbose=True)
sitl_args = ['--model', 'quad', ]
sitl.launch(sitl_args, await_ready=True, restart=True)
connection_string = sitl.connection_string()

vehicle = connect(connection_string)