//#attribute indent = _utils.Indent(4, True)

void function()
{
//#template block(level, max)
	printf("nested level ${level}");$>
//#	{if level < max:

	{
		$<${indent.indent(block(level + 1, max))}
	}$>
//#	}
//# end template
}

//#template make_function(name, max_indent)
void $name()
{
	$<${block(0, max_indent)}
}
//#end template
