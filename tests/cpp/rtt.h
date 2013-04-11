#include "types.h"

namespace game { namespace rtt {

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
	virtual int* cast(void*, int*) const {return 0;}
	virtual float* cast(void*, float*) const {return 0;}
	virtual vector* cast(void*, vector*) const {return 0;}
	virtual transform* cast(void*, transform*) const {return 0;}
	virtual object* cast(void*, object*) const {return 0;}
};

//Forward decl
class typeinfo_int;
class typeinfo_float;
class typeinfo_vector;
class typeinfo_transform;
class typeinfo_object;

inline typeinfo_int const* get_type(int const*);
inline typeinfo_float const* get_type(float const*);
inline typeinfo_vector const* get_type(vector const*);
inline typeinfo_transform const* get_type(transform const*);
inline typeinfo_object const* get_type(object const*);

class typeinfo_int : public typeinfo_base
{
public:
	static unsigned int const TYPEID = 0;

	typeinfo_int()
	{
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return 0;}
	
	virtual typeinfo_base const* field_type(size_t) const {return 0;}
	virtual char const* field_name(size_t) const {return 0;}
	virtual void* get_field(void*, size_t) const {return 0;}

protected:
	virtual int* cast(void* p, int*) const {return static_cast<int*>(p);}

private:
};
class typeinfo_float : public typeinfo_base
{
public:
	static unsigned int const TYPEID = 1;

	typeinfo_float()
	{
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return 0;}
	
	virtual typeinfo_base const* field_type(size_t) const {return 0;}
	virtual char const* field_name(size_t) const {return 0;}
	virtual void* get_field(void*, size_t) const {return 0;}

protected:
	virtual float* cast(void* p, float*) const {return static_cast<float*>(p);}

private:
};
class typeinfo_vector : public typeinfo_base
{
public:
	static unsigned int const TYPEID = 2;

	typeinfo_vector()
	{
		m_types[0] = get_type((float*)(0));
		m_names[0] = "x";
		m_types[1] = get_type((float*)(0));
		m_names[1] = "y";
		m_types[2] = get_type((float*)(0));
		m_names[2] = "z";
		m_types[3] = get_type((float*)(0));
		m_names[3] = "w";
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return 4;}
	
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
			case 0:
				return &static_cast<vector*>(p)->x;
			case 1:
				return &static_cast<vector*>(p)->y;
			case 2:
				return &static_cast<vector*>(p)->z;
			case 3:
				return &static_cast<vector*>(p)->w;
			default:
				return 0; //no field found
		}
	}

protected:
	virtual vector* cast(void* p, vector*) const {return static_cast<vector*>(p);}

private:
	typeinfo_base const* m_types[4];
	char const* m_names[4];
};
class typeinfo_transform : public typeinfo_base
{
public:
	static unsigned int const TYPEID = 3;

	typeinfo_transform()
	{
		m_types[0] = get_type((vector*)(0));
		m_names[0] = "forward";
		m_types[1] = get_type((vector*)(0));
		m_names[1] = "up";
		m_types[2] = get_type((vector*)(0));
		m_names[2] = "left";
		m_types[3] = get_type((vector*)(0));
		m_names[3] = "position";
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return 4;}
	
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
			case 0:
				return &static_cast<transform*>(p)->forward;
			case 1:
				return &static_cast<transform*>(p)->up;
			case 2:
				return &static_cast<transform*>(p)->left;
			case 3:
				return &static_cast<transform*>(p)->position;
			default:
				return 0; //no field found
		}
	}

protected:
	virtual transform* cast(void* p, transform*) const {return static_cast<transform*>(p);}

private:
	typeinfo_base const* m_types[4];
	char const* m_names[4];
};
class typeinfo_object : public typeinfo_base
{
public:
	static unsigned int const TYPEID = 4;

	typeinfo_object()
	{
		m_types[0] = get_type((int*)(0));
		m_names[0] = "health";
		m_types[1] = get_type((transform*)(0));
		m_names[1] = "xform";
	}

	virtual unsigned int get_id() const {return TYPEID;}

	virtual size_t field_count() const {return 2;}
	
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
			case 0:
				return &static_cast<object*>(p)->health;
			case 1:
				return &static_cast<object*>(p)->xform;
			default:
				return 0; //no field found
		}
	}

protected:
	virtual object* cast(void* p, object*) const {return static_cast<object*>(p);}

private:
	typeinfo_base const* m_types[2];
	char const* m_names[2];
};

struct type_lib
{
	typeinfo_base* types[5];
};

static type_lib* s_lib = 0;

template <class T> struct type_traits;

template <> struct type_traits<int>
{
	typedef typeinfo_int info_type;
	static unsigned int const id = 0;
};

inline typeinfo_int const* get_type(int const*)
	{return static_cast<typeinfo_int const*>(s_lib->types[0]);}

template <> struct type_traits<float>
{
	typedef typeinfo_float info_type;
	static unsigned int const id = 1;
};

inline typeinfo_float const* get_type(float const*)
	{return static_cast<typeinfo_float const*>(s_lib->types[1]);}

template <> struct type_traits<vector>
{
	typedef typeinfo_vector info_type;
	static unsigned int const id = 2;
};

inline typeinfo_vector const* get_type(vector const*)
	{return static_cast<typeinfo_vector const*>(s_lib->types[2]);}

template <> struct type_traits<transform>
{
	typedef typeinfo_transform info_type;
	static unsigned int const id = 3;
};

inline typeinfo_transform const* get_type(transform const*)
	{return static_cast<typeinfo_transform const*>(s_lib->types[3]);}

template <> struct type_traits<object>
{
	typedef typeinfo_object info_type;
	static unsigned int const id = 4;
};

inline typeinfo_object const* get_type(object const*)
	{return static_cast<typeinfo_object const*>(s_lib->types[4]);}

void create()
{
	s_lib = new type_lib();
	typeinfo_base** types = s_lib->types;
	types[0] = new typeinfo_int();
	types[1] = new typeinfo_float();
	types[2] = new typeinfo_vector();
	types[3] = new typeinfo_transform();
	types[4] = new typeinfo_object();
}

void destroy()
{
	typeinfo_base** types = s_lib->types;

	for(unsigned int i = 0; i < 5; ++i)
	{
		delete types[i];
		types[i] = 0;
	}

	delete s_lib;
	s_lib = 0;
}

}} //namespace

