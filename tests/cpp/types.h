namespace game
{
	struct vector
	{
		float x;
		float y;
		float z;
		float w;
	};
	struct transform
	{
		vector forward;
		vector up;
		vector left;
		vector position;
	};
	struct object
	{
		int health;
		transform xform;
	};
}

