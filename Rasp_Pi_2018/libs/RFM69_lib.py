# The MIT License (MIT)
#
# Copyright (c) 2018 Margaret Johnson for fun.
# Copyright (c) 2017 Tony DiCola for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`RFM69_Pi`
====================================================

Very primitive Raspberry Pi RFM69 packet radio module. This is mostly Tony DiCola's
code.  The major changes are in handling SPI and using an interrupt for knowing when
a send or receive is completed.  The rest of this text comes from Tony's CircuitPython
implementation.

This supports basic RadioHead-compatible sending and
receiving of packets with RFM69 series radios (433/915Mhz).

.. note:: This does NOT support advanced RadioHead features like guaranteed delivery--only 'raw'
    packets are currently supported.

.. warning:: This is NOT for LoRa radios!

.. note:: This is a 'best effort' at receiving data using pure Python code--there is not interrupt
    support so you might lose packets if they're sent too quickly for the board to process them.
    You will have the most luck using this in simple low bandwidth scenarios like sending and
    receiving a 60 byte packet at a time--don't try to receive many kilobytes of data at a time!

* Author(s): Tony DiCola
"""
import os
import sys
LIB_PATH = os.environ['LADYBUG_LIB_PATH']
from handle_logging_lib import HandleLogging
import RPi.GPIO as GPIO
import spidev
import time


__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RFM69.git"


# pylint: disable=bad-whitespace
# Internal constants:
_REG_FIFO = 0x00
_REG_OP_MODE = 0x01
_REG_DATA_MOD = 0x02
_REG_BITRATE_MSB = 0x03
_REG_BITRATE_LSB = 0x04
_REG_FDEV_MSB = 0x05
_REG_FDEV_LSB = 0x06
_REG_FRF_MSB = 0x07
_REG_FRF_MID = 0x08
_REG_FRF_LSB = 0x09
_REG_VERSION = 0x10
_REG_PA_LEVEL = 0x11
_REG_RX_BW = 0x19
_REG_AFC_BW = 0x1A
_REG_RSSI_VALUE = 0x24
_REG_DIO_MAPPING1 = 0x25    # mapping of pins DIO0 to DIO3
_REG_IRQ_FLAGS1 = 0x27
_REG_IRQ_FLAGS2 = 0x28
_REG_PREAMBLE_MSB = 0x2C
_REG_PREAMBLE_LSB = 0x2D
_REG_SYNC_CONFIG = 0x2E
_REG_SYNC_VALUE1 = 0x2F
_REG_PACKET_CONFIG1 = 0x37
_REG_FIFO_THRESH = 0x3C
_REG_PACKET_CONFIG2 = 0x3D
_REG_AES_KEY1 = 0x3E
_REG_TEMP1 = 0x4E
_REG_TEMP2 = 0x4F
_REG_TEST_PA1 = 0x5A
_REG_TEST_PA2 = 0x5C
_REG_TEST_DAGC = 0x6F

_TEST_PA1_NORMAL = 0x55
_TEST_PA1_BOOST = 0x5D
_TEST_PA2_NORMAL = 0x70
_TEST_PA2_BOOST = 0x7C

# The crystal oscillator frequency and frequency synthesizer step size.
# See the datasheet for details of this calculation.
_FXOSC = 32000000.0
_FSTEP = _FXOSC / 524288

# RadioHead specific compatibility constants.
_RH_BROADCAST_ADDRESS = 0xFF

# User facing constants:
SLEEP_MODE = 0b000
STANDBY_MODE = 0b001
FS_MODE = 0b010
TX_MODE = 0b011
RX_MODE = 0b100
# pylint: enable=bad-whitespace

# Disable the silly too many instance members warning.  Pylint has no knowledge
# of the context and is merely guessing at the proper amount of members.  This
# is a complex chip which requires exposing many attributes and state.  Disable
# the warning to work around the error.
# pylint: disable=too-many-instance-attributes


class RFM69:
    """Interface to a RFM69 series packet radio.  Allows simple sending and
    receiving of wireless data at supported frequencies of the radio
    (433/915mhz).

    :param busio.SPI spi: The SPI bus connected to the chip.  Ensure SCK, MOSI, and MISO are
        connected.
    :param ~digitalio.DigitalInOut cs: A DigitalInOut object connected to the chip's CS/chip select
        line.
    :param ~digitalio.DigitalInOut reset: A DigitalInOut object connected to the chip's RST/reset
        line.
    :param int frequency: The center frequency to configure for radio transmission and reception.
        Must be a frequency supported by your hardware (i.e. either 433 or 915mhz).
    :param bytes sync_word: A byte string up to 8 bytes long which represents the syncronization
        word used by received and transmitted packets. Read the datasheet for a full understanding
        of this value! However by default the library will set a value that matches the RadioHead
        Arduino library.
    :param int preamble_length: The number of bytes to pre-pend to a data packet as a preamble.
        This is by default 4 to match the RadioHead library.
    :param bytes encryption_key: A 16 byte long string that represents the AES encryption key to use
        when encrypting and decrypting packets.  Both the transmitter and receiver MUST have the
        same key value! By default no encryption key is set or used.
    :param bool high_power: Indicate if the chip is a high power variant that supports boosted
        transmission power.  The default is True as it supports the common RFM69HCW modules sold by
        Adafruit.

    .. note:: The D0/interrupt line is currently unused by this module and can remain unconnected.

    Remember this library makes a best effort at receiving packets with pure Python code.  Trying
    to receive packets too quickly will result in lost data so limit yourself to simple scenarios
    of sending and receiving single packets at a time.

    Also note this library tries to be compatible with raw RadioHead Arduino library communication.
    This means the library sets up the radio modulation to match RadioHead's default of GFSK
    encoding, 250kbit/s bitrate, and 250khz frequency deviation. To change this requires explicitly
    setting the radio's bitrate and encoding register bits. Read the datasheet and study the init
    function to see an example of this--advanced users only! Advanced RadioHead features like
    address/node specific packets or guaranteed delivery are not supported. Only simple broadcast
    of packets to all listening radios is supported. Features like addressing and guaranteed
    delivery need to be implemented at an application level.
    """

    class _RegisterBits:
        # Class to simplify access to the many configuration bits avaialable
        # on the chip's registers.  This is a subclass here instead of using
        # a higher level module to increase the efficiency of memory usage
        # (all of the instances of this bit class will share the same buffer
        # used by the parent RFM69 class instance vs. each having their own
        # buffer and taking too much memory).

        # Quirk of pylint that it requires public methods for a class.  This
        # is a decorator class in Python and by design it has no public methods.
        # Instead it uses dunder accessors like get and set below.  For some
        # reason pylint can't figure this out so disable the check.
        # pylint: disable=too-few-public-methods

        # Again pylint fails to see the true intent of this code and warns
        # against private access by calling the write and read functions below.
        # This is by design as this is an internally used class.  Disable the
        # check from pylint.
        # pylint: disable=protected-access

        def __init__(self, address, *, offset=0, bits=1):
            assert 0 <= offset <= 7
            assert 1 <= bits <= 8
            assert (offset + bits) <= 8
            self._address = address
            self._mask = 0
            for _ in range(bits):
                self._mask <<= 1
                self._mask |= 1
            self._mask <<= offset
            self._offset = offset

        def __get__(self, obj, objtype):
            reg_value = obj._read_u8(self._address)
            return (reg_value & self._mask) >> self._offset

        def __set__(self, obj, val):
            reg_value = obj._read_u8(self._address)
            reg_value &= ~self._mask
            reg_value |= (val & 0xFF) << self._offset
            obj._write_u8(self._address, reg_value)

    # Control bits from the registers of the chip:
    data_mode = _RegisterBits(_REG_DATA_MOD, offset=5, bits=2)

    modulation_type = _RegisterBits(_REG_DATA_MOD, offset=3, bits=2)

    modulation_shaping = _RegisterBits(_REG_DATA_MOD, offset=0, bits=2)

    temp_start = _RegisterBits(_REG_TEMP1, offset=3)

    temp_running = _RegisterBits(_REG_TEMP1, offset=2)

    sync_on = _RegisterBits(_REG_SYNC_CONFIG, offset=7)

    sync_size = _RegisterBits(_REG_SYNC_CONFIG, offset=3, bits=3)

    aes_on = _RegisterBits(_REG_PACKET_CONFIG2, offset=0)

    pa_0_on = _RegisterBits(_REG_PA_LEVEL, offset=7)

    pa_1_on = _RegisterBits(_REG_PA_LEVEL, offset=6)

    pa_2_on = _RegisterBits(_REG_PA_LEVEL, offset=5)

    output_power = _RegisterBits(_REG_PA_LEVEL, offset=0, bits=5)

    rx_bw_dcc_freq = _RegisterBits(_REG_RX_BW, offset=5, bits=3)

    rx_bw_mantissa = _RegisterBits(_REG_RX_BW, offset=3, bits=2)

    rx_bw_exponent = _RegisterBits(_REG_RX_BW, offset=0, bits=3)

    afc_bw_dcc_freq = _RegisterBits(_REG_AFC_BW, offset=5, bits=3)

    afc_bw_mantissa = _RegisterBits(_REG_AFC_BW, offset=3, bits=2)

    afc_bw_exponent = _RegisterBits(_REG_AFC_BW, offset=0, bits=3)

    packet_format = _RegisterBits(_REG_PACKET_CONFIG1, offset=7, bits=1)

    dc_free = _RegisterBits(_REG_PACKET_CONFIG1, offset=5, bits=2)

    crc_on = _RegisterBits(_REG_PACKET_CONFIG1, offset=4, bits=1)

    crc_auto_clear_off = _RegisterBits(_REG_PACKET_CONFIG1, offset=3, bits=1)

    address_filter = _RegisterBits(_REG_PACKET_CONFIG1, offset=1, bits=2)

    mode_ready = _RegisterBits(_REG_IRQ_FLAGS1, offset=7)

    rx_ready = _RegisterBits(_REG_IRQ_FLAGS1, offset=6)

    tx_ready = _RegisterBits(_REG_IRQ_FLAGS1, offset=5)

    dio_0_mapping = _RegisterBits(_REG_DIO_MAPPING1, offset=6, bits=2)

    packet_sent = _RegisterBits(_REG_IRQ_FLAGS2, offset=3)

    payload_ready = _RegisterBits(_REG_IRQ_FLAGS2, offset=2)

    def __init__(self, *, reset=22, intPin=18, frequency=915, sync_word=b'\x2D\xD4',
                 preamble_length=4, encryption_key=None, high_power=True, baudrate=2000000):
        self.handle_logging = HandleLogging()
        self.callback = None
        self._tx_power = 13
        self.high_power = high_power
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        # initialize SPI
        self._device = spidev.SpiDev()
        self._device.open(0, 0)
        self._device.max_speed_hz = baudrate
        self._device.mode = 0
        self._reset = reset
        GPIO.setup(self._reset, GPIO.OUT)
        self._intPin = intPin
        GPIO.setup(self._intPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.remove_event_detect(self._intPin)
        GPIO.add_event_detect(self._intPin, GPIO.RISING, callback=self.interruptHandler)
        # Reset the chip.
        self.reset()
        # Check the version of the chip.
        version = self._read_u8(_REG_VERSION)
        if version != 0x24:
            raise RuntimeError('Failed to find RFM69 with expected version, check wiring!')
        # Enter idle state.
        self.idle()
        # Setup the chip in a similar way to the RadioHead RFM69 library.
        # Set FIFO TX condition to not empty and the default FIFO threshold
        # to 15.
        self._write_u8(_REG_FIFO_THRESH, 0b10001111)
        # Configure low beta off.
        self._write_u8(_REG_TEST_DAGC, 0x30)
        # Disable boost.
        self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
        self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        # Set the syncronization word.
        self.sync_word = sync_word
        # Configure modulation for RadioHead library GFSK_Rb250Fd250 mode
        # by default.  Users with advanced knowledge can manually reconfigure
        # for any other mode (consulting the datasheet is absolutely
        # necessary!).
        self.data_mode = 0b00              # Packet mode
        self.modulation_type = 0b00        # FSK modulation
        self.modulation_shaping = 0b01     # Gaussian filter, BT=1.0
        self.bitrate = 250000              # 250kbs
        self.frequency_deviation = 250000  # 250khz
        self.rx_bw_dcc_freq = 0b111        # RxBw register = 0xE0
        self.rx_bw_mantissa = 0b00
        self.rx_bw_exponent = 0b000
        self.afc_bw_dcc_freq = 0b111       # AfcBw register = 0xE0
        self.afc_bw_mantissa = 0b00
        self.afc_bw_exponent = 0b000
        self.packet_format = 1             # Variable length.
        self.dc_free = 0b10                # Whitening
        self.crc_on = 1                    # CRC enabled
        self.crc_auto_clear = 0            # Clear FIFO on CRC fail
        self.address_filtering = 0b00      # No address filtering
        # Set the preamble length.
        self.preamble_length = preamble_length
        # Set frequency.
        self.frequency = frequency
        # Set encryption key.
        self.encryption_key = encryption_key
        # Set transmit power to 13 dBm, a safe value any module supports.
        self.tx_power = 13
        # Set to True in _get_packet when a packet is received.
        self.packet_received = False

    def _read_into(self, address, buf, length=None):
        # buf is a bytearray that we'll fill with the list of bytes returned
        # from the SPI read...
        # Read a number of bytes from the specified address into the provided
        # buffer.  If length is not specified (the default) the entire buffer
        # will be filled.
        if length is None:
            length = len(buf)
        resp = self._device.xfer([address & 0x7F])
        buf = b''.join(resp)

    def _read_u8(self, address):
        # Read a single byte from the provided address and return it.
        address = address & 0x7F  # Strip out top bit to set 0
        # value (read).
        resp = self._device.xfer([address, 0x00])  # the second byte doesn't matter.  Just
        # needs to be there...
        return resp[1]  # the return byte is in the 2nd element.

    def _write_from(self, address, buf, length=None):
        # From what I can tell, buf is a 2 byte byte array...
        # Write a number of bytes to the provided address and taken from the
        # provided buffer.  If no length is specified (the default) the entire
        # buffer is written.
        if length is None:
            length = len(buf)
        stuff_to_send = [address | 0x80] + list(buf)
        self._device.xfer(stuff_to_send)

    def _write_u8(self, address, value):
        address = (address | 0x80) & 0xFF  # Set top bit to 1 to indicate write
        value = value & 0xFF
        self._device.xfer([address, value])

    def reset(self):
        """Perform a reset of the chip."""
        GPIO.output(self._reset, GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(self._reset, GPIO.LOW)
        time.sleep(0.005)

    def idle(self):
        """Enter idle standby mode (switching off high power amplifiers if necessary)."""
        # Like RadioHead library, turn off high power boost if enabled.
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        self.operation_mode = STANDBY_MODE

    def sleep(self):
        """Enter sleep mode."""
        self.operation_mode = SLEEP_MODE

    def listen(self):
        """Listen for packets to be received by the chip.  Use :py:func:`receive` to listen, wait
           and retrieve packets as they're available.
        """
        # Like RadioHead library, turn off high power boost if enabled.
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        # Enable payload ready interrupt for D0 line.
        self.dio_0_mapping = 0b01
        # Enter RX mode (will clear FIFO!).
        self.operation_mode = RX_MODE

    def transmit(self):
        """Transmit a packet which is queued in the FIFO.  This is a low level function for
           entering transmit mode and more.  For generating and transmitting a packet of data use
           :py:func:`send` instead.
        """
        # Like RadioHead library, turn on high power boost if enabled.
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_BOOST)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_BOOST)
        # Enable packet sent interrupt for D0 line.
        self.dio_0_mapping = 0b00
        # Enter TX mode (will clear FIFO!).
        self.operation_mode = TX_MODE
        # In case we hang in this loop, we'll set a time to break out.
        timeout = time.time() + 5
        while not self.packet_sent:
            if time.time() > timeout:
                self.handle_logging.print_error("Timed out trying to send packet!")
                break
            pass

    @property
    def temperature(self):
        """The internal temperature of the chip in degrees Celsius. Be warned this is not
           calibrated or very accurate.

           .. warning:: Reading this will STOP any receiving/sending that might be happening!
        """
        # Start a measurement then poll the measurement finished bit.
        self.temp_start = 1
        while self.temp_running > 0:
            pass
        # Grab the temperature value and convert it to Celsius.
        # This uses the same observed value formula from the Radiohead library.
        temp = self._read_u8(_REG_TEMP2)
        return 166.0 - temp

    @property
    def operation_mode(self):
        """The operation mode value.  Unless you're manually controlling the chip you shouldn't
           change the operation_mode with this property as other side-effects are required for
           changing logical modes--use :py:func:`idle`, :py:func:`sleep`, :py:func:`transmit`,
           :py:func:`listen` instead to signal intent for explicit logical modes.
        """
        op_mode = self._read_u8(_REG_OP_MODE)
        return (op_mode >> 2) & 0b111

    @operation_mode.setter
    def operation_mode(self, val):
        assert 0 <= val <= 4
        # Set the mode bits inside the operation mode register.
        op_mode = self._read_u8(_REG_OP_MODE)
        op_mode &= 0b11100011
        op_mode |= (val << 2)
        self._write_u8(_REG_OP_MODE, op_mode)
        # Wait for mode to change by polling interrupt bit.
        while not self.mode_ready:
            pass

    @property
    def sync_word(self):
        """The synchronization word value.  This is a byte string up to 8 bytes long (64 bits)
           which indicates the synchronization word for transmitted and received packets. Any
           received packet which does not include this sync word will be ignored. The default value
           is 0x2D, 0xD4 which matches the RadioHead RFM69 library. Setting a value of None will
           disable synchronization word matching entirely.
        """
        # Handle when sync word is disabled..
        if not self.sync_on:
            return None
        # Sync word is not disabled so read the current value.
        sync_word_length = self.sync_size + 1  # Sync word size is offset by 1
        # according to datasheet.
        sync_word = bytearray(sync_word_length)
        self._read_into(_REG_SYNC_VALUE1, sync_word)
        return sync_word

    @sync_word.setter
    def sync_word(self, val):
        # Handle disabling sync word when None value is set.
        if val is None:
            self.sync_on = 0
        else:
            # Check sync word is at most 8 bytes.
            assert 1 <= len(val) <= 8
            # Update the value, size and turn on the sync word.
            self._write_from(_REG_SYNC_VALUE1, val)
            self.sync_size = len(val) - 1  # Again sync word size is offset by
            # 1 according to datasheet.
            self.sync_on = 1

    @property
    def preamble_length(self):
        """The length of the preamble for sent and received packets, an unsigned 16-bit value.
           Received packets must match this length or they are ignored! Set to 4 to match the
           RadioHead RFM69 library.
        """
        msb = self._read_u8(_REG_PREAMBLE_MSB)
        lsb = self._read_u8(_REG_PREAMBLE_LSB)
        return ((msb << 8) | lsb) & 0xFFFF

    @preamble_length.setter
    def preamble_length(self, val):
        assert 0 <= val <= 65535
        self._write_u8(_REG_PREAMBLE_MSB, (val >> 8) & 0xFF)
        self._write_u8(_REG_PREAMBLE_LSB, val & 0xFF)

    @property
    def frequency_mhz(self):
        """The frequency of the radio in Megahertz. Only the allowed values for your radio must be
           specified (i.e. 433 vs. 915 mhz)!
        """
        # FRF register is computed from the frequency following the datasheet.
        # See section 6.2 and FRF register description.
        # Read bytes of FRF register and assemble into a 24-bit unsigned value.
        msb = self._read_u8(_REG_FRF_MSB)
        mid = self._read_u8(_REG_FRF_MID)
        lsb = self._read_u8(_REG_FRF_LSB)
        frf = ((msb << 16) | (mid << 8) | lsb) & 0xFFFFFF
        frequency = (frf * _FSTEP) / 1000000.0
        return frequency

    @frequency_mhz.setter
    def frequency_mhz(self, val):
        assert 290 <= val <= 1020
        # Calculate FRF register 24-bit value using section 6.2 of the datasheet.
        frf = int((val * 1000000.0) / _FSTEP) & 0xFFFFFF
        # Extract byte values and update registers.
        msb = frf >> 16
        mid = (frf >> 8) & 0xFF
        lsb = frf & 0xFF
        self._write_u8(_REG_FRF_MSB, msb)
        self._write_u8(_REG_FRF_MID, mid)
        self._write_u8(_REG_FRF_LSB, lsb)

    @property
    def encryption_key(self):
        """The AES encryption key used to encrypt and decrypt packets by the chip. This can be set
           to None to disable encryption (the default), otherwise it must be a 16 byte long byte
           string which defines the key (both the transmitter and receiver must use the same key
           value).
        """
        # Handle if encryption is disabled.
        if self.aes_on == 0:
            return None
        # Encryption is enabled so read the key and return it.
        key = bytearray(16)
        self._read_into(_REG_AES_KEY1, key)
        return key

    @encryption_key.setter
    def encryption_key(self, val):
        # Handle if unsetting the encryption key (None value).
        if val is None:
            self.aes_on = 0
        else:
            # Set the encryption key and enable encryption.
            assert len(val) == 16
            self._write_from(_REG_AES_KEY1, val)
            self.aes_on = 1

    @property
    def tx_power(self):
        """The transmit power in dBm. Can be set to a value from -2 to 20 for high power devices
           (RFM69HCW, high_power=True) or -18 to 13 for low power devices. Only integer power
           levels are actually set (i.e. 12.5 will result in a value of 12 dBm).
        """
        # Follow table 10 truth table from the datasheet for determining power
        # level from the individual PA level bits and output power register.
        pa0 = self.pa_0_on
        pa1 = self.pa_1_on
        pa2 = self.pa_2_on
        if pa0 and not pa1 and not pa2:
            # -18 to 13 dBm range
            return -18 + self.output_power
        elif not pa0 and pa1 and not pa2:
            # -2 to 13 dBm range
            return -18 + self.output_power
        elif not pa0 and pa1 and pa2 and not self.high_power:
            # 2 to 17 dBm range
            return -14 + self.output_power
        elif not pa0 and pa1 and pa2 and self.high_power:
            # 5 to 20 dBm range
            return -11 + self.output_power
        else:
            raise RuntimeError('Power amplifiers in unknown state!')

    @tx_power.setter
    def tx_power(self, val):
        val = int(val)
        # Determine power amplifier and output power values depending on
        # high power state and requested power.
        pa_0_on = 0
        pa_1_on = 0
        pa_2_on = 0
        output_power = 0
        if self.high_power:
            # Handle high power mode.
            assert -2 <= val <= 20
            if val <= 13:
                pa_1_on = 1
                output_power = val + 18
            elif 13 < val <= 17:
                pa_1_on = 1
                pa_2_on = 1
                output_power = val + 14
            else:  # power >= 18 dBm
                # Note this also needs PA boost enabled separately!
                pa_1_on = 1
                pa_2_on = 1
                output_power = val + 11
        else:
            # Handle non-high power mode.
            assert -18 <= val <= 13
            # Enable only power amplifier 0 and set output power.
            pa_0_on = 1
            output_power = val + 18
        # Set power amplifiers and output power as computed above.
        self.pa_0_on = pa_0_on
        self.pa_1_on = pa_1_on
        self.pa_2_on = pa_2_on
        self.output_power = output_power
        self._tx_power = val

    @property
    def rssi(self):
        """The received strength indicator (in dBm) of the last received message."""
        # Read RSSI register and convert to value using formula in datasheet.
        return -self._read_u8(_REG_RSSI_VALUE)/2.0

    @property
    def bitrate(self):
        """The modulation bitrate in bits/second (or chip rate if Manchester encoding is enabled).
           Can be a value from ~489 to 32mbit/s, but see the datasheet for the exact supported
           values.
        """
        msb = self._read_u8(_REG_BITRATE_MSB)
        lsb = self._read_u8(_REG_BITRATE_LSB)
        return _FXOSC / ((msb << 8) | lsb)

    @bitrate.setter
    def bitrate(self, val):
        assert (_FXOSC/65535) <= val <= 32000000.0
        # Round up to the next closest bit-rate value with addition of 0.5.
        bitrate = int((_FXOSC / val) + 0.5) & 0xFFFF
        self._write_u8(_REG_BITRATE_MSB, bitrate >> 8)
        self._write_u8(_REG_BITRATE_LSB, bitrate & 0xFF)

    @property
    def frequency_deviation(self):
        """The frequency deviation in Hertz."""
        msb = self._read_u8(_REG_FDEV_MSB)
        lsb = self._read_u8(_REG_FDEV_LSB)
        return _FSTEP * ((msb << 8) | lsb)

    @frequency_deviation.setter
    def frequency_deviation(self, val):
        assert 0 <= val <= (_FSTEP*16383)  # fdev is a 14-bit unsigned value
        # Round up to the next closest integer value with addition of 0.5.
        fdev = int((val / _FSTEP) + 0.5) & 0x3FFF
        self._write_u8(_REG_FDEV_MSB, fdev >> 8)
        self._write_u8(_REG_FDEV_LSB, fdev & 0xFF)

    def send(self, data_string):
        """Send a string of data using the transmitter.  You can only send 60 bytes at a time
           (limited by chip's FIFO size and appended headers). Note this appends a 4 byte header to
           be compatible with the RadioHead library.
        """
        assert 0 < len(data_string) <= 60
        # pylint: enable=len-as-condition
        self.idle()  # Stop receiving to clear FIFO and keep it clear.
        stuff_to_send = [_REG_FIFO | 0x80]  # Set top bit to 1 to indicate a write.
        # Add 4 bytes for  RadhioHead Library
        stuff_to_send += [(len(data_string) + 4) & 0xFF]
        # Send over broadcast address.
        stuff_to_send += [_RH_BROADCAST_ADDRESS, _RH_BROADCAST_ADDRESS]
        # Add txHeaderId and txHeaderFlag bytes
        stuff_to_send += [0, 0]
        # Add in the data
        if isinstance(data_string, str):
            stuff_to_send += [int(ord(i)) for i in list(data_string)]
        else:  # assume bytearray...
            stuff_to_send += [i for i in list(data_string)]
        self._device.xfer(stuff_to_send)
        # Turn on transmit mode to send out the packet.
        self.transmit()

        self.idle()

    def receive_begin(self, timeout_s=5, keep_listening=True, callback=None):
        """Wait to receive a packet from the receiver. Will wait for up to timeout_s amount of
           seconds for a packet to be received and decoded. If a packet is found the payload bytes
           are returned, otherwise None is returned (which indicates the timeout elapsed with no
           reception). Note this assumes a 4-byte header is prepended to the data for compatibilty
           with the RadioHead library (the header is not validated nor returned). If keep_listening
           is True (the default) the chip will immediately enter listening mode after reception of
           a packet, otherwise it will fall back to idle mode and ignore any future reception.
        """
        # Make sure we are listening for packets.
        start_time = time.time()
        self.callback = callback
        self.packet_received = False
        while True:
            self.listen()
            # packet received is set when a packet comes in via the interrupt.
            if self.packet_received or time.time() - start_time > timeout_s:
                if keep_listening is False:
                    self.idle()
                    break

    def _get_packet(self):
        address = _REG_FIFO
        fifo_length, targetid, senderid, byte1, byte2 = self._device.xfer(
            [_REG_FIFO & 0x7f, 0, 0, 0, 0, 0])[1:]
        fifo_length -= 4
        received_data = bytearray(self._device.xfer([_REG_FIFO & 0x7f] +
                                                    [0 for i in range(0, fifo_length)])[1:])
        if (self.callback):
            self.listen()
            self.packet_received = True
            self.callback(received_data)

    def interruptHandler(self, int):
        if self.payload_ready:
            self.idle()
            self._get_packet()
        else:
            self.listen()
