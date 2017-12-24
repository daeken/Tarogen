using System;
using System.Collections.Generic;

namespace CpuBase {
	public abstract class InstructionClass<InsnT> {
		public abstract bool Match(InsnT insn);
	}

	[AttributeUsage(AttributeTargets.Method)]
	public abstract class InstructionAttribute : Attribute {
		public abstract Type InstructionType { get; }
	}

	public abstract class Registers<DataT> {
		protected abstract int Count { get; }

		public DataT this[uint index] {
			get {
				throw new NotImplementedException();
			}
			set {
				throw new NotImplementedException();
			}
		}
	}
	
	public abstract class Cpu<PtrT> where PtrT : struct {
		protected T IFetch<T>(PtrT? addr = null) {
			throw new NotImplementedException();
		}

		protected IEnumerable<T> GetInstructions<T>() {
			throw new NotImplementedException();
		}

		protected T ToSigned<T>(ulong value) {
			throw new NotImplementedException();
		}
		protected T ToUnsigned<T>(long value) {
			throw new NotImplementedException();
		}

		protected bool TryExecute<InsnT>(InsnT insn) {
			throw new NotImplementedException();
		}

		public abstract bool Dispatch(PtrT pc);
		public abstract void DidOverflow();
	}
}