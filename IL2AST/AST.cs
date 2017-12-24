using System.Collections;
using System.Collections.Generic;
using System.Linq;
using MoreLinq;
using static System.Console;

namespace IL2AST {
	public abstract class AstNode {
		protected virtual string[] Elements => null;
		protected virtual string[] PythonElements => Elements;

		public override string ToString() => string.Join(" ", Elements ?? new string[0]);
		public virtual string ToPython() => $"{GetType().Name}({string.Join(", ", PythonElements ?? new string[0])})";
	}

	public class ListNode : AstNode, IEnumerable<AstNode> {
		readonly List<AstNode> children = new List<AstNode>();

		public IEnumerator<AstNode> GetEnumerator() => children.GetEnumerator();
		IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

		public override string ToString() => $"({Indent(string.Join("\n", children))})";
		public override string ToPython() => $"ListNode({Indent(string.Join("\n", children.Select(x => x.ToPython() + ", ")))})";

		public void Add(AstNode node) => node?.Pass(children.Add);
		public void Add(ListNode node) => ((AstNode) node)?.Pass(children.Add);
		public void Add(IEnumerable<AstNode> nodes) => nodes.ForEach(x => x?.Pass(children.Add));
		public void Add(string value) => value?.Pass(x => children.Add((SymbolNode) x));

		static string Indent(string val) {
			if(val.Length == 0)
				return "";
			var elems = val.Split('\n');
			if(elems.Length == 1)
				return val;
			return elems[0] + "\n" + string.Join("\n", elems.Skip(1).Select(x => $"  {x}"));
		}
	}

	public class DataNode : AstNode {
		public readonly byte[] Data;

		public DataNode(byte[] data) => Data = data;

		protected override string[] Elements => Data.Select(x => $"0x{x:X2}").ToArray();
		protected override string[] PythonElements => Elements;
	}

	public class StringNode : AstNode {
		public readonly string Data;

		public StringNode(string data) => Data = data;

		protected override string[] Elements => new [] { "\"" + Data.Replace("\\", "\\\\").Replace("\n", "\\n").Replace("\r", "\\r") + "\"" };
	}

	public class SymbolNode : AstNode {
		public readonly string Data;

		public SymbolNode(string data) => Data = data;

		protected override string[] Elements => new [] { Data };
		protected override string[] PythonElements => new [] { "\"" + Data.Replace("\\", "\\\\").Replace("\n", "\\n").Replace("\r", "\\r") + "\"" };
		
		public static implicit operator SymbolNode(string data) => new SymbolNode(data);
	}

	public class SignedNode : AstNode {
		public readonly long Value;

		public SignedNode(long value) => Value = value;

		protected override string[] Elements => new[] { $"0x{Value:X}" };
	}

	public class UnsignedNode : AstNode {
		public readonly ulong Value;

		public UnsignedNode(ulong value) => Value = value;

		protected override string[] Elements => new[] { $"0x{Value:X}U" };
		protected override string[] PythonElements => new[] { $"0x{Value:X}" };
	}
}

