
namespace texthon {

struct type_lib
{
 	int get_typeid(int* t)
	{
		return 0;
	}
};

struct type_info
{
	unsigned int field_count;

	void* get_field(void* ptr, unsigned int field);
	type_info const* get_field_type(void* ptr, unsigned int field);

	virtual void on_visit(void* p)
	{
		T* actual = static_cast<T>(p);

	}
};

template <class T> T* lib::try_cast(type_info const& type, void* ptr)
{
	id = type.lib.map<T>;
}

}
