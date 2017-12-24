using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;
using Mono.Cecil.Rocks;
using MoreLinq;
using static System.Console;

namespace IL2AST {
	public static class ILConverter {
		static SymbolNode Symbol(string value) => new SymbolNode(value);
		static StringNode String(string value) => new StringNode(value);
		
		public static AstNode Convert(Type type) {
			var mod = ModuleDefinition.ReadModule(type.Assembly.Location);
			var types = mod.Types.Where(x => x.Namespace == type.Namespace);
			return new ListNode {
				"namespace", 
				type.Namespace, 
				types.Select(Process)
			};
		}

		static AstNode Process(TypeDefinition type) => 
			new ListNode {
				type.IsClass ? "class" : "struct", 
				type.Name, 
				new ListNode { type.BaseType?.Pass(x => x is GenericInstanceType ? Process((GenericInstanceType) x) : Process(x)) }, 
				type.CustomAttributes.Select(Process), 
				type.Fields.Select(Process), 
				type.Properties.Select(Process),
				type.Methods.Select(Process)
			};

		static AstNode Process(TypeReference tr) =>
			new ListNode {
				"type", 
				tr.Name
			};

		static AstNode Process(GenericInstanceType tr) =>
			new ListNode {
				"type", 
				tr.Name, 
				tr.GenericArguments.Select(Process)
			};

		static AstNode Process(FieldDefinition field) =>
			new ListNode {
				"field", 
				field.Name, 
				Process(field.FieldType)
			};

		static AstNode Process(PropertyDefinition prop) =>
			new ListNode {
				"property", 
				prop.Name, 
				Process(prop.PropertyType), 
				prop.GetMethod?.Pass(Process, false), 
				prop.SetMethod?.Pass(Process, false) 
			};

		static AstNode Process(MethodDefinition meth) => Process(meth, noHidden: true);
		static AstNode Process(MethodDefinition meth, bool noHidden) =>
			meth.IsCompilerControlled && noHidden
				? null
				: new ListNode {
					"method", 
					meth.Name, 
					new ListNode {
						Process(meth.ReturnType), 
						meth.Parameters.Select(Process)
					}, 
					meth.CustomAttributes.Select(Process), 
					meth.Body.Pass(Process)
				};

		static AstNode Process(MethodBody body) =>
			new ListNode {
				"body", 
				body.Instructions.Select(x => new ListNode {
					new SignedNode(x.Offset), 
					x.OpCode.Name, 
					x.Operand?.Pass(ProcessOperand)
				})
			};

		static AstNode ProcessOperand(object op) {
			switch(op) {
				case Instruction inst:
					return new SignedNode(inst.Offset);
				case MethodDefinition methd:
					return new ListNode {
						"method",
						ProcessOperand(methd.DeclaringType), 
						new ListNode { methd.Name }, 
						ProcessOperand(methd.ReturnType), 
						methd.Parameters.Select(ProcessOperand)
					};
				case GenericInstanceMethod imethd:
					return new ListNode {
						"method",
						ProcessOperand(imethd.DeclaringType), 
						new ListNode { imethd.Name, imethd.GenericArguments.Select(ProcessOperand) }, 
						ProcessOperand(imethd.ReturnType), 
						imethd.Parameters.Select(ProcessOperand)
					};
				case MethodReference mr:
					return new ListNode {
						"method", 
						ProcessOperand(mr.DeclaringType), 
						new ListNode { mr.Name },
						ProcessOperand(mr.ReturnType), 
						mr.Parameters.Select(ProcessOperand)
					};
				case GenericInstanceType git:
					return new ListNode {
						"type", 
						git.Name, 
						git.GenericArguments.Select(ProcessOperand)
					};
				case TypeDefinition td:
					return new ListNode {
						"type", 
						td.Name, 
					};
				case GenericParameter gp:
					return new ListNode {
						"type", 
						gp.FullName
					};
				case ParameterDefinition pd:
					return ProcessOperand(pd.ParameterType);
				case TypeReference tr:
					return new ListNode {
						"type", 
						tr.Name
					};
				case FieldDefinition fd:
					return new ListNode {
						"field", 
						ProcessOperand(fd.DeclaringType), 
						fd.Name, 
						ProcessOperand(fd.FieldType)
					};
				case VariableDefinition vd:
					return new ListNode {
						"variable", 
						new UnsignedNode((ulong) vd.Index), 
						ProcessOperand(vd.VariableType)
					};
				default:
					return ProcessValue(op);
			}
		}

		static AstNode Process(MethodReference meth) =>
			new ListNode {
				"method", 
				meth.Name
			};

		static AstNode Process(ParameterDefinition param) =>
			new ListNode {
				param.Name,
				Process(param.ParameterType)
			};
		
		static AstNode Process(CustomAttribute param) {
			return new ListNode {
				"attribute", 
				param.Constructor.DeclaringType.Name, 
				param.ConstructorArguments.Select(Process)
			};
		}

		static AstNode Process(CustomAttributeArgument arg) => ProcessValue(arg.Value);

		static AstNode Process(byte[] data) => new DataNode(data);

		static AstNode ProcessValue(object obj) {
			switch(obj) {
				case string str:
					return new StringNode(str);
				case sbyte sbval:
					return new SignedNode(sbval);
				case short sval:
					return new SignedNode(sval);
				case int ival:
					return new SignedNode(ival);
				case long lval:
					return new SignedNode(lval);
				case byte bval:
					return new UnsignedNode(bval);
				case ushort usval:
					return new UnsignedNode(usval);
				case uint uival:
					return new UnsignedNode(uival);
				case ulong ulval:
					return new UnsignedNode(ulval);
				default:
					WriteLine($"Unknown object type to ProcessValue: {obj.GetType()}");
					WriteLine(obj);
					return null;
			}
		}
	}
}