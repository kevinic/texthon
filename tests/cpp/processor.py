def norm(types):
	typeId = 0
	for type in types:
		type["id"] = typeId

		if "extern" not in type:
			type["extern"] = False
		if "members" not in type:
			type["members"] = []

		typeId += 1
