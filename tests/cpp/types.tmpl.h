//#template make_types(name, types)
namespace $name
{
//#	{for type in types:
//#		{if not type["extern"]:
	struct ${type["name"]}
	{
//#			{for member in type["members"]:
		${member[0]} ${member[1]};
//#			}
	};
//#		}
//#	}
}
//#end template

