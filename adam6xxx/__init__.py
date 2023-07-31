# -*- coding: utf-8 -*-
import enum
import time
from typing import List

from pymodbus.client import ModbusTcpClient


class Edges(enum.IntEnum):
    RISING = enum.auto()
    FALLING = enum.auto()


class ADAM6XXX:
    """
    Base class for the ADAM-6000 series I/O modules
    """
    ip: str = '10.0.0.1'
    name: str = ''
    connected = False

    digital_outputs: List[int] = []
    digital_inputs: List[int] = []
    analog_outputs: List[int] = []
    analog_outputs: List[int] = []
    counter_registers: List[int] = []
    pulse_low_widths: List[int] = []
    pulse_high_widths: List[int] = []
    absolute_pulse_count: List[int] = []
    incremental_pulse_count: List[int] = []
    output_diagnostics: int
    module_name: int = 210
    gcl_flags: int = 304
    gcl_counter_registers: List[int] = [310, 312, 314, 316, 318, 320, 322, 324]
    clear_gcl_counters = [300, 301, 302, 303, 304, 305, 306, 307]

    def __init__(self, ip: str = '10.0.0.1', connect: bool = False):
        """
        Create a new ADAM-6000 object.

        This should not be called directly; use one of the module-specific objects.

        Args:
            ip (str, optional): IP address of module. Defaults to '10.0.0.1'.
            connect (bool, optional): Whether to connect to the module on construction. Defaults to False.
        """
        self.ip = ip
        self._client = ModbusTcpClient(self.ip)
        if connect:
            self.connect()

    def connect(self) -> bool:
        """
        Connect to the module

        Returns:
            bool: Whether the connection was successful
        """
        self.connected = self._client.connect()
        self.get_module_name()
        return self.connected

    def set_digital_output(self, index: int, state: bool, verify: bool = True) -> None:
        """
        Set a digital output on the module

        Args:
            index (int): Which output to set
            state (bool): Whether to set the output HIGH (True) or LOW (False)
            verify (bool, optional): Whether to query the output state to verify the change took. Defaults to True.

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        self._client.write_coil(
            address=self.digital_outputs[index], value=state)
        if verify:
            coil_state = self.get_digital_output(index)
            assert (coil_state == state)

    def get_digital_output(self, index: int) -> bool:
        """
        Read the state of a digital output

        Args:
            index (int): Which output to read

        Returns:
            bool: Output state, HIGH (True) or LOW (False)

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        return self._client.read_coils(address=self.digital_outputs[index]).bits[0]

    def get_digital_input(self, index: int) -> bool:
        """
        Read the state of a digital input

        Args:
            index (int): Which input to read

        Returns:
            bool: Input state, HIGH (True) or LOW (False)

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        return self._client.read_discrete_inputs(address=self.digital_inputs[index])

    def pulse_digital_output(self, index: int, polarity: Edges = Edges.RISING, verify: bool = True, duration: float = 0.1) -> None:
        """
        Perform a software-controlled pulse of an output

        Args:
            index (int): Which output to pulse
            polarity (Edges, optional): Which direction the pulse should be. Defaults to Edges.RISING.
            verify (bool, optional): Whether to query the output state to verify the change took. Defaults to True.
            duration (float, optional): Duration in seconds for the pulse. Defaults to 0.1.

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        assert (polarity in Edges)
        if polarity == Edges.RISING:
            self.set_digital_output(index, False, verify)
            self.set_digital_output(index, True, verify)
            time.sleep(duration)
            self.set_digital_output(index, False, verify)
        elif polarity == Edges.FALLING:
            self.set_digital_output(index, True, verify)
            self.set_digital_output(index, False, verify)
            time.sleep(duration)
            self.set_digital_output(index, True, verify)

    def get_module_name(self) -> str:
        """
        Retrieve the module model name

        Returns:
            str: The module model name

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        low, high = self._client.read_input_registers(
            address=self.module_name, count=2).registers
        self.name = ''
        if low:
            self.name = self.name + hex(low)[2:]
        if high:
            self.name = self.name + hex(high)[2:]
        return self.name

    def get_counter(self, index: int) -> int:
        """
        Get the value of one of the input counters

        Args:
            index (int): The index of counter to read

        Returns:
            int: the value of the counter (high * 65536 + low)

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        low, high = self._client.read_input_registers(
            address=self.counter_registers[index], count=2).registers
        return high * 65536 + low

    def get_frequency(self, index: int) -> float:
        """
        Get the value of one of the input frequency registers

        Args:
            index (int): The index of register to read

        Returns:
            float: the value of the register in Hertz (low/10.0Hz)

        Raises:
            pymodbus.exceptions.ConnectionException if the module is not responding
        """
        low = self._client.read_input_registers(
            address=self.counter_registers[index], count=1).registers
        return low / 10.0


class ADAM6052(ADAM6XXX):
    """
    Class covering the ADAM-6052 8-input/8-output digital module
    """
    digital_inputs = [0, 1, 2, 3, 4, 5, 6, 7]
    digital_outputs = [16, 17, 18, 19, 20, 21, 22, 23]
    counter_registers = [0, 2, 4, 6, 8, 10, 12, 14]
    pulse_low_widths = [16, 18, 20, 22, 24, 26, 28, 30]
    pulse_high_widths = [32, 34, 36, 38, 40, 42, 44, 46]
    absolute_pulse_count = [48, 50, 52, 54, 56, 58, 60, 62]
    incremental_pulse_count = [64, 66, 68, 70, 72, 74, 76, 78]
    output_diagnostics = 306


class ADAM6060(ADAM6XXX):
    """
    Class covering the ADAM-6060 6-input/6-relay-output digital module
    """
    digital_inputs = [0, 1, 2, 3, 4, 5]
    digital_outputs = [16, 17, 18, 19, 20, 21]
    counter_registers = [0, 2, 4, 6, 8, 10]
    pulse_low_widths = [12, 14, 16, 18, 20, 22]
    pulse_high_widths = [24, 26, 28, 30, 32, 34]
    absolute_pulse_count = [36, 38, 40, 42, 44, 46]
    incremental_pulse_count = [48, 50, 52, 54, 56, 58]
