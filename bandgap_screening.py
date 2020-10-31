#!/usr/bin/env python3

import json
import os
import sys

from pymatgen.core.periodic_table import Element
from pymatgen import MPRester

#from mprester_bulk_query import bulk_query

try:
	from pydash import chunk as get_chunks
except ImportError:
	from math import ceil
	def get_chunks(array, size=1):
		chunks = int(ceil(len(array) / float(size)))
		return [array[i * size:(i + 1) * size]
			for i in range(chunks)]

try:
	from tqdm import tqdm as PBar
except ImportError:
	class PBar():
		def __init__(self, total):
			self.total = total
			self.done = 0
			self.report()
		def update(self, amount):
			self.done += amount
			self.report()
		def report(self):
			print("{} of {} done {:.1%}".format(self.done, self.total, self.done/self.total))

def bulk_query(self, criteria, properties, chunk_size=100, **kwargs):
	data = []
	mids = [d["material_id"] for d in
		self.query(criteria, ["material_id"])]
	chunks = get_chunks(mids, size=chunk_size)
	progress_bar = PBar(total=len(mids))
	if not isinstance(criteria, dict):
		criteria = self.parse_criteria(criteria)
	for chunk in chunks:
		chunk_criteria = criteria.copy()
		chunk_criteria.update({"material_id": {"$in": chunk}})
		data.extend(self.query(chunk_criteria, properties, **kwargs))
		progress_bar.update(len(chunk))
	return data

MPRester.bulk_query = bulk_query

TARGET_DIR = "./your_directory"

if __name__ == "__main__":
# mkdir
	if not os.path.exists(TARGET_DIR):
		os.mkdir(TARGET_DIR)

# exclude elements
	exclude_z = [2,10,18,36,54,86]  # 18 group
	#exclude_z += list(i for i in range(6, 11))  # from C to Ne
	#exclude_z += list(i for i in range(15, 19))  # from P to Ar
	#exclude_z += list(i for i in range(34, 37))  # from Se to Kr
	exclude_z += list(i for i in range(91, 103))  # from Pa to Lr
	exclude_list = [str(Element.from_Z(z)) for z in exclude_z]
	#exclude_list.remove("O")

# query
	with MPRester("YOUR_API_KEY") as m:
		prop_to_get = list(MPRester.supported_properties)
		# Elasticity has Structure object and can't be simply dumped to json
		prop_to_get.remove("elasticity")

		#mag_threshold = 1e-2
		materials = m.bulk_query({"nelements": {"$gte": 1},
                                  "elements": {#"$in": ["O"],
                                               "$nin": list(exclude_list)},
                                  #"spacegroup.number": {"$in":[1,3,4,5,6,7,8,9,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,75,76,77,78,79,80,81,82,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,168,169,170,171,172,173,174,177,178,179,180,181,182,183,184,185,186,187,188,189,190,195,196,197,198,199,207,208,209,210,211,212,213,214,215,216,217,218,219,220]},
                                  "spacegroup.number": {"$in": list(range(1,231))},
                                  "band_gap": {"$gte": 0.1},
                                  #"total_magnetization": {"$lte": mag_threshold,
                                   #                       "$gte": -mag_threshold},
                                  #"nsites": {"$lte": 40}
                                  # "bandstructure" : {"has"}
},
                                 prop_to_get,
                                 chunk_size=100)
		for mat in materials:
			with open("{}/{}.json".format(TARGET_DIR, mat["material_id"]), "w") as fw:
				try:
					json.dump(mat, fw, indent=2)
				except:
					print("{} was Failed".format(mat['material_id']))
					print("-"*50)
					print(mat)
					print("\n")
