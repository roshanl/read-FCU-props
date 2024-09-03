import sys
import asyncio
import json
from typing import Callable, Dict, Any
from bacpypes3.settings import settings
from bacpypes3.debugging import bacpypes_debugging, ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.pdu import Address
from bacpypes3.lib.batchread import DeviceAddressObjectPropertyReference, BatchRead

# some debugging
_debug = 0
_log = ModuleLogger(globals())

# globals
app: Application
batch_read: BatchRead

@bacpypes_debugging
class SampleCmd:
    """
    Sample Cmd
    """

    def __init__(self, results: Dict[str, Any]):
        self.results = results

    async def read(self) -> None:
        """
        Trigger batch read and collect results.
        """
        if _debug:
            SampleCmd._debug("read")

        await batch_read.run(app, self.callback)

    def callback(self, key, value) -> None:
        # Store the result in the dictionary
        self.results[key] = value

    def stop(self) -> None:
        global batch_read
        batch_read.stop()


async def read_batches() -> str:
    global app, batch_read

    # Dictionary to hold results
    results = {}

    try:
        parser = SimpleArgumentParser()

        if _debug:
            _log.debug("settings: %r", settings)
        parser.add_argument(
            "device_address",
            help="address of the server (B-device)",
        )
        args = parser.parse_args()
        app = Application.from_args(args)
        device_address = args.device_address
        stuff_to_read = [
            ("Fan Status", Address(device_address), "binary-value,5", "present-value"),
            ("System Enable", Address(device_address), "binary-value,40", "present-value"),
            ("Keypad Lock", Address(device_address), "analog-value,128", "present-value"),
            ("Occupied Setpoint", Address(device_address), "analog-value,90", "present-value"),
            ("Occupied Stpt Hi Limit", Address(device_address), "analog-value,91", "present-value"),
            ("Occupied Stpt Lo Limit", Address(device_address), "analog-value,92", "present-value"),
            ("Heating Offset", Address(device_address), "analog-value,94", "present-value"),
            ("Cooling Offset", Address(device_address), "analog-value,93", "present-value"),
            ("Cooling Valve", Address(device_address), "analog-output,0", "present-value"),
            ("Electric Heater", Address(device_address), "analog-output,1", "present-value"),
            ("Fan Speed", Address(device_address), "analog-value,16", "present-value"),
            ("1- Low Speed", Address(device_address), "binary-output,0", "present-value"),
            ("2-Med. Speed", Address(device_address), "binary-output,1", "present-value"),
            ("3 - High Speed", Address(device_address), "binary-output,2", "present-value"),
            ("Space Temp", Address(device_address), "analog-value,104", "present-value"),
            ("Space Humidity", Address(device_address), "analog-value,105", "present-value"),
            ("Discharge Air Flow", Address(device_address), "binary-value,5", "present-value"),
        ]
        # Transform the list of stuff to read
        daopr_list = [
            DeviceAddressObjectPropertyReference(*args) for args in stuff_to_read
        ]
        batch_read = BatchRead(daopr_list)

        # Create and run the command
        cmd = SampleCmd(results)
        await cmd.read()


    finally:
        if app:
            app.close()

    # Convert the results dictionary to a JSON string
    return json.dumps(results, indent=4)


async def main() -> None:
    # Call the function and get the results as JSON
    json_result = await read_batches()

    # Output the JSON result
    print(json_result)


if __name__ == "__main__":
    asyncio.run(main())
