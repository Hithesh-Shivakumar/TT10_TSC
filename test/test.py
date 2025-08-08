# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

@cocotb.test()
async def test_trivium_stream_processor(dut):
    """Test Trivium-lite stream processing with reversible transformation"""
    
    dut._log.info("Starting Trivium-lite stream processor test")
    
    # Clock period is 20 ns (50 MHz)
    clock = Clock(dut.clk, 20, units="ns")
    cocotb.start_soon(clock.start())
    
    # Test vectors
    input_data = [0xDE, 0xAD, 0xBE, 0xEF]
    intermediate = [0] * 4
    output_data = [0] * 4
    
    # Input Initialization
    dut.ena.value = 1
    dut.ui_in.value = 0x00
    dut.uio_in.value = 0x00
    
    # Reset sequence
    dut._log.info("Reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 3)
    dut.rst_n.value = 1
    
    # === SEED INPUT ===
    dut._log.info("Setting seed")
    dut.uio_in.value = 0x76
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 1)
    
    # === FIRST PASS ===
    dut._log.info("=== First Pass ===")
    for i in range(4):
        dut.ui_in.value = input_data[i]
        await ClockCycles(dut.clk, 8)
        intermediate[i] = int(dut.uo_out.value)
        dut._log.info(f"Input[{i}] = 0x{input_data[i]:02x} => Intermediate = 0x{intermediate[i]:02x}")
    
    # === RESET STATE ===
    dut._log.info("Resetting for second pass")
    dut.uio_in.value = 0xFF
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 2)
    
    # === SAME SEED ===
    dut._log.info("Reapplying seed")
    dut.uio_in.value = 0x76
    await ClockCycles(dut.clk, 1)
    dut.uio_in.value = 0x00
    await ClockCycles(dut.clk, 1)
    
    # === SECOND PASS ===
    dut._log.info("=== Second Pass ===")
    for i in range(4):
        dut.ui_in.value = intermediate[i]
        await ClockCycles(dut.clk, 8)
        output_data[i] = int(dut.uo_out.value)
        dut._log.info(f"Intermediate[{i}] = 0x{intermediate[i]:02x} => Output = 0x{output_data[i]:02x}")
    
    # === CHECK ===
    dut._log.info("=== Test Result ===")
    all_passed = True
    for i in range(4):
        if input_data[i] == output_data[i]:
            dut._log.info(f"PASS: [{i}] 0x{input_data[i]:02x} -> 0x{intermediate[i]:02x} -> 0x{output_data[i]:02x}")
        else:
            dut._log.error(f"FAIL: [{i}] 0x{input_data[i]:02x} -> 0x{intermediate[i]:02x} -> 0x{output_data[i]:02x}")
            all_passed = False
    
    # Final assertion
    assert all_passed, "Test failed - output data doesn't match original input"
    
    dut._log.info("Trivium-lite stream processor test completed successfully")
