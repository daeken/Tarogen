using System;

namespace IL2AST {
	public static class Extensions {
		public static RetT Pass<ParamT, Param2T, RetT>(this ParamT param, Func<ParamT, Param2T, RetT> func, Param2T _2) => func(param, _2);
		public static RetT Pass<ParamT, RetT>(this ParamT param, Func<ParamT, RetT> func) => func(param);
		public static void Pass<ParamT>(this ParamT param, Action<ParamT> func) => func(param);
	}
}