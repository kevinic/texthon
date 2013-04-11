//#template make_rtt(name, types)
#include "types.h"

//#	!type_count = len(types)
namespace $name { namespace rtt {

class typeinfo_base
{
public:
	virtual ~typeinfo_base() {}
	virtual unsigned int get_id() const = 0;

	virtual size_t field_count() const = 0;
	virtual typeinfo_base const* field_type(size_t index) const = 0;
	virtual char const* field_name(size_t index) const = 0;
	virtual void* get_field(void* p, size_t index) const = 0;

	template <class T> T* cast(void* p) const
	{
		T* t = 0;
		return cast(p, t);
	}

protected:
//#	{for type in types:
//#		!name = type["name"]
	virtual $name* cast(void*, $name*) const {return 0;}
//#	}
};

//Forward decl
//#	{for type in types:
//#		!name = type["name"]
class typeinfo_$name;
//# }

//#	{for type in types:
//#		!name = type["name"]
inline typeinfo_$name const* get_type($name const*);
//# }

//#	{for type in types:
//#		!name = type["name"]
//#		!field_count = len(type["members"])
class typeinfo_$name : public typeinfo_base
{
public:
	static unsigned int const TYPEID = ${type["id"]};

	typeinfo_$name()
	{
//#		!index = 0;
//#		{for member in type["members"]:
//#			!(member_type, member_name) = member
		m_types[$index] = get_type(($member_type*)(0));
		m_names[$index] = "$member_name";
//#			!index += 1
//#		}
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return $field_count;}
	
//#		{if field_count:
	virtual typeinfo_base const* field_type(size_t index) const
	{
		return m_types[index];
	}

	virtual char const* field_name(size_t index) const
	{
		return m_names[index];
	};

	virtual void* get_field(void* p, size_t index) const
	{
		switch(index)
		{
//#			!index = 0;
//#			{for member in type["members"]:
			case $index:
				return &static_cast<$name*>(p)->${member[1]};
//#				!index += 1
//# 		}
			default:
				return 0; //no field found
		}
	}
//#		}
//#		{else:
	virtual typeinfo_base const* field_type(size_t) const {return 0;}
	virtual char const* field_name(size_t) const {return 0;}
	virtual void* get_field(void*, size_t) const {return 0;}
//#		}

protected:
	virtual $name* cast(void* p, $name*) const {return static_cast<$name*>(p);}

private:
//#		{if field_count:
	typeinfo_base const* m_types[$field_count];
	char const* m_names[$field_count];
//#		}
};
//#	}

struct type_lib
{
	typeinfo_base* types[$type_count];
};

static type_lib* s_lib = 0;

template <class T> struct type_traits;
//#	{for type in types:
//#		!name = type["name"]
//#		!id = type["id"]

template <> struct type_traits<$name>
{
	typedef typeinfo_$name info_type;
	static unsigned int const id = $id;
};

inline typeinfo_$name const* get_type($name const*)
	{return static_cast<typeinfo_$name const*>(s_lib->types[$id]);}
//#	}

void create()
{
	s_lib = new type_lib();
	typeinfo_base** types = s_lib->types;
//#	{for type in types:
//#		!name = type["name"]
//#		!id = type["id"]
	types[$id] = new typeinfo_$name();
//#	}
}

void destroy()
{
	typeinfo_base** types = s_lib->types;

	for(unsigned int i = 0; i < $type_count; ++i)
	{
		delete types[i];
		types[i] = 0;
	}

	delete s_lib;
	s_lib = 0;
}

}} //namespace
//#end template

