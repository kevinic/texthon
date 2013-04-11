#include "rtt.h"
#include <stdio.h>

using namespace game;

void print_r(unsigned int level, char const* name, rtt::typeinfo_base const* type, void* ptr)
{
	for(unsigned int i = 0; i < level; ++i)
	{
		printf(" ");
	}

	switch(type->get_id())
	{
	case rtt::type_traits<float>::id:
		printf("%s: %f\n", name, *type->cast<float>(ptr));
		break;

	case rtt::type_traits<int>::id:
		printf("%s: %i\n", name, *type->cast<int>(ptr));
		break;

	default:
		printf("%s:\n", name);
		for(unsigned int field = 0; field < type->field_count(); ++field)
		{
			print_r(level + 1, type->field_name(field), type->field_type(field), type->get_field(ptr, field));
		}
		break;
	}
}

template <class T> void print(T& obj)
{
	print_r(0, "obj", rtt::get_type(&obj), &obj);
}

int main(int, char**)
{
	rtt::create();

	transform trans = {
		{0, 0, 1, 0},
		{0, 1, 0, 0},
		{1, 0, 0, 0},
		{0, 0, 0, 1},
	};
	object obj;
	obj.health = 100;
	obj.xform = trans;
	print(obj);

	rtt::destroy();
	return 0;
}
