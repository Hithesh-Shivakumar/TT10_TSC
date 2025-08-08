# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def tt_um_trivium_stream_processor(dut):
    """Trivium-lite stream processor interface activity test"""

    dut._log.info("Starting Trivium-lite stream processor test")

    # Clock period is 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, units="ns")
    cocotb.start_soon(clock.start())

    # Basic init
    dut.ena.value = 1
    dut.ui_in.value = 0x00
    dut.uio_in.value = 0x00
    dut.rst_n.value = 0

    # Reset pulse
    dut._log.info("Applying reset")
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # Send seed
    dut._log.info("Sending seed")
    dut.uio_in.value = 0x76
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 1)

    # First pass
    dut._log.info("Starting first pass")
    for i in range(4):
        dut.ui_in.value = i
        await ClockCycles(dut.clk, 8)
        dut._log.info(f"Cycle {i} completed")

    # Reset again
    dut._log.info("Resetting internal state")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)

    # Same seed
    dut._log.info("Reapplying seed")
    dut.uio_in.value = 0x76
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 1)

    # Second pass
    dut._log.info("Starting second pass")
    for i in range(4):
        dut.ui_in.value = i + 10
        await ClockCycles(dut.clk, 8)
        dut._log.info(f"Cycle {i} completed")

    # Done
    dut._log.info("Test completed successfully")
