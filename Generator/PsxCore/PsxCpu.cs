using System;
using CpuBase;
using static System.Console;

namespace Generator.PsxCore {
	class IType : InstructionClass<IType> {
		public byte Op, Rs, Rt;
		public ushort Imm;
		
		public static IType Parse(uint inst) {
			for(var i = 0; i < 100; ++i) {
				if(i < 50)
					WriteLine(i);
				else
					WriteLine(i + 10);
			}
			return new IType {
				Op = inst.Bitfield<byte>(31, 26), 
				Rs = inst.Bitfield<byte>(25, 21), 
				Rt = inst.Bitfield<byte>(20, 16), 
				Imm = inst.Bitfield<ushort>(15, 0) 
			};
		}
		
		public override bool Match(IType insn) {
			return insn.Op == Op;
		}
	}
	
	class ITypeAttribute : InstructionAttribute {
		public override Type InstructionType => typeof(IType);

		public ITypeAttribute(byte op, string disasm) {
		}
	}

	class RType : InstructionClass<RType> {
		public byte Op, Rs, Rt, Rd = 5, Shamt, Funct;

		public static RType Parse(uint inst) {
			return new RType {
				Op = inst.Bitfield<byte>(31, 26), 
				Rs = inst.Bitfield<byte>(25, 21), 
				Rt = inst.Bitfield<byte>(20, 16), 
				Rd = inst.Bitfield<byte>(15, 11),  
				Shamt = inst.Bitfield<byte>(10, 6),  
				Funct = inst.Bitfield<byte>(5, 0)  
			};
		}

		public override bool Match(RType insn) {
			return insn.Op == Op && insn.Funct == Funct;
		}
	}
	
	class RTypeAttribute : InstructionAttribute {
		public override Type InstructionType => typeof(RType);

		public RTypeAttribute(byte op, string disasm) {
		}
	}

	public class PsxRegs : Registers<uint> {
		protected override int Count => 32;
	}
	
	public class PsxCpu : Cpu<uint> {
		PsxRegs Gpr;
		
		public override bool Dispatch(uint pc) {
			var insn = IFetch<uint>();
			
			if(TryExecute(IType.Parse(insn)))
				return true;
			if(TryExecute(RType.Parse(insn)))
				return true;

			WriteLine($"Unhandled instruction: {insn : X8} {insn}");
			return false;
		}

		public override void DidOverflow() {
		}

		[RType(0b100_000, "add %$rd, %$rs, %$rt")]
		void Add(RType insn) {
			Gpr[insn.Rd] = checked(Gpr[insn.Rs].ToSigned() + Gpr[insn.Rt].ToSigned()).ToUnsigned();
		}

		[IType(0b001_000, "addi %$rt, %$rs, $imm")]
		void AddI(IType insn) {
			Gpr[insn.Rt] = checked(Gpr[insn.Rs].ToSigned() + insn.Imm.ToSigned()).ToUnsigned();
		}
	}
}