import sys
import os.path

HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
ADD  = 0b10100000
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256

        self.reg = [0] * 8

        self.pc = 0 # Program Counter
        self.ir = 0 # Instruction Register
        self.mar = 0 # Memory Address Register
        self.mdr = 0 # Memory Data Register
        self.fl = 0 # Flag Register
        self.halted = False

        self.reg[7] = 0xF4

        self.branchtable = {}
        self.branchtable[HLT] = self.execute_HLT
        self.branchtable[LDI] = self.execute_LDI
        self.branchtable[PRN] = self.execute_PRN
        self.branchtable[MUL] = self.execute_MUL
        self.branchtable[PUSH] = self.execute_PUSH
        self.branchtable[POP] = self.execute_POP
        self.branchtable[CALL] = self.execute_CALL
        self.branchtable[RET] = self.execute_RET
        self.branchtable[CMP] = self.execute_CMP
        self.branchtable[JMP] = self.execute_JMP
        self.branchtable[JEQ] = self.execute_JEQ
        self.branchtable[JNE] = self.execute_JNE
        self.branchtable[ADD] = self.execute_ADD

    @property
    def sp(self):
        return self.reg[7]

    @sp.setter
    def sp(self, a):
        self.reg[7] = a & 0xFF

    @property
    def operand_a(self):
        return self.ram_read(self.pc + 1)

    @property
    def operand_b(self):
        return self.ram_read(self.pc + 2)

    @property
    def instruction_size(self):
        return ((self.ir >> 6) & 0b11) + 1

    @property
    def instruction_sets_pc(self):
        return ((self.ir >> 4) & 0b0001) == 1

    def ram_read(self, mar):
        if mar >= 0 and mar < len(self.ram):
            return self.ram[mar]
        else:
            print(f"Error: Attempted to read from memory address: {mar}.")
            return -1

    def ram_write(self, mar, mdr):
        if mar >= 0 and mar < len(self.ram):
            self.ram[mar] = mdr & 0xFF
        else:
            print(f"Error: Attempted to write to memory address: {mar}.")

    def load(self, file_name):
        """Load a program into memory."""
        address = 0

        file_path = os.path.join(os.path.dirname(__file__), file_name)
        try:
            with open(file_path) as f:
                for line in f:
                    num = line.split("#")[0].strip()
                    try:
                        instruction = int(num, 2)
                        self.ram[address] = instruction
                        address += 1
                    except:
                        continue
        except:
            print(f'Could not find file named: {file_name}')
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while not self.halted:

            self.ir = self.ram_read(self.pc)

            if self.ir in self.branchtable:
                self.branchtable[self.ir]()
            else:
                print(f"Error: Could not find instruction: {self.ir} in branch table.")
                sys.exit(1)

            if not self.instruction_sets_pc:
                self.pc += self.instruction_size

    def execute_HLT(self):
        self.halted = True

    def execute_LDI(self):
        self.reg[self.operand_a] = self.operand_b

    def execute_PRN(self):
        print(self.reg[self.operand_a])

    def execute_MUL(self):
        self.reg[self.operand_a] *= self.reg[self.operand_b]

    def execute_PUSH(self):
        self.sp -= 1
        self.mdr = self.reg[self.operand_a]
        self.ram_write(self.sp, self.mdr)

    def execute_POP(self):
        self.mdr = self.ram_read(self.sp)
        self.reg[self.operand_a] = self.mdr
        self.sp += 1

    def execute_CALL(self):
        self.sp -= 1
        self.ram_write(self.sp, self.pc + self.instruction_size)
        self.pc = self.reg[self.operand_a]

    def execute_RET(self):
        self.pc = self.ram_read(self.sp)
        self.sp += 1

    def execute_ADD(self):
        self.reg[self.operand_a] += self.reg[self.operand_b]
    
    def execute_CMP(self):
        if self.reg[self.operand_a] < self.reg[self.operand_b]:
            self.fl = 0b00000100
        elif self.reg[self.operand_a] > self.reg[self.operand_b]:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000001

    def execute_JMP(self):
        self.pc = self.reg[self.operand_a]

    def execute_JEQ(self):
        if self.fl == 0b00000001:
            self.execute_JMP()
        else:
            self.pc += self.instruction_size

    def execute_JNE(self):
        if self.fl != 0b00000001:
            self.execute_JMP()
        else:
            self.pc += self.instruction_size 
