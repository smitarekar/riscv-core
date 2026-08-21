RTL := $(wildcard ../rtl/*.v)
PROGRAMS := arithmetic sum_loop loadstore macc_single macc_dot_product macc_overflow
HEXFILES := $(addprefix ../tb/programs/,$(addsuffix .hex,$(PROGRAMS)))

.PHONY: sim unit programs golden wave clean

# Full-core integration test (assembles programs, runs all unit tests, the
# core, then cross-checks the MACC results against the Python golden model)
sim: programs unit
	cd .. && iverilog -o sim/core.vvp $(RTL:../%=%) tb/tb_riscv_core.v
	cd .. && vvp sim/core.vvp
	$(MAKE) golden

# Independent from `sim` above: re-derives expected MACC values from the
# raw instruction words (golden_model.py) instead of trusting the
# hardcoded constants in tb_riscv_core.v, and diffs them against what the
# simulation actually printed. See tb/check_against_golden.py.
golden:
	cd .. && python3 tb/check_against_golden.py

programs: $(HEXFILES)

../tb/programs/%.hex: ../tb/programs/%.s ../tb/programs/asm_to_hex.py
	python3 ../tb/programs/asm_to_hex.py $< $@

# Per-module unit testbenches
unit:
	cd .. && iverilog -o sim/tb_alu.vvp rtl/alu.v tb/tb_alu.v && vvp sim/tb_alu.vvp
	cd .. && iverilog -o sim/tb_regfile.vvp rtl/regfile.v tb/tb_regfile.v && vvp sim/tb_regfile.vvp
	cd .. && iverilog -o sim/tb_imm_gen.vvp rtl/imm_gen.v tb/tb_imm_gen.v && vvp sim/tb_imm_gen.vvp
	cd .. && iverilog -o sim/tb_control_unit.vvp rtl/control_unit.v tb/tb_control_unit.v && vvp sim/tb_control_unit.vvp
	cd .. && iverilog -o sim/tb_pc.vvp rtl/program_counter.v tb/tb_pc.v && vvp sim/tb_pc.vvp
	cd .. && iverilog -o sim/tb_data_mem.vvp rtl/data_mem.v tb/tb_data_mem.v && vvp sim/tb_data_mem.vvp
	cd .. && iverilog -o sim/tb_mac_unit.vvp rtl/mac_unit.v tb/tb_mac_unit.v && vvp sim/tb_mac_unit.vvp

wave: sim
	cd .. && gtkwave core.vcd &

clean:
	rm -f *.vvp ../tb/programs/*.hex
