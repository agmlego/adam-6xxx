# ADAM-6000 Series Module

Python module to wrap the Modbus/TCP functions of the Advantech ADAM-6000 series I/O devices.

## Examples

```python
from adam6xxx import ADAM6052

adam = ADAM6052(ip='198.51.100.1', connect=True)

# Turn on an output
adam.set_digital_output(index=0, state=True)

# Read an input
result = adam.get_digital_input(index=0)

# Read a counter value
counter = adam.get_counter(index=2)
```