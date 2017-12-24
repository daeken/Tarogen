using System;
using System.Collections.Generic;
using System.IO;
using Generator.PsxCore;
using IL2AST;
using static System.Console;

namespace Generator {
	internal class Program {
		public static void Main(string[] args) {
			WriteLine($"from ast import *\nroot = {ILConverter.Convert(typeof(PsxCpu)).ToPython()}");
		}
	}
}