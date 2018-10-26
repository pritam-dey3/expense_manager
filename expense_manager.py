import pymongo, datetime
from pprint import pprint


def create():
	def add_member(n):
		member_collection.update_one(
			{"name": n},
	        {
	            "$setOnInsert": {"name": n},
	        },
	        upsert=True)

	name = "*"
	print("Enter names of the members...")
	while name:
		name = input("||: ")
		if name:
			add_member(name)
	return True

def end():
	return False

def spend():
	def proper_input(l):
		[n, v] = l #needs modification here
		exist = member_collection.find_one({"name": n})
		v_c = True
		try:
			v = float(v)
		except ValueError:
			v_c = False
		cond = (bool(exist) and v_c)
		return (cond,n,v)

	while True:
		cause = input("\nCause ||: ")
		if not expense_collection.find_one({"cause": cause}):
			break
		print("\nGiven Cause already exists! Try another...\n")
	while True:
		n_a = input("\nSpent By (Name and Amount) ||: ") #multiple donators
		c, spent_by, self_exp = proper_input(n_a.split())
		if c:
			break
		else:
			print("\ninvalid input. try again...")

	print("\nEnter Name(s) and Amount(s):\n")
	spent_for = []
	mbr = "*"
	while mbr:
		mbr = input("||: ")
		if not mbr:
			break
		c, name, value = proper_input(mbr.split())
		if c:
			spent_for.append({"name": name,"value": value})
		else:
			print("\ninvalid input. try again...\n")
	
	input_doc = {
		"_id": expense_collection.count(),
		"cause": cause,
		"date": str(datetime.datetime.now()),
		"spent_by": spent_by,
		"spent_for": spent_for,
		"self": self_exp - sum([d["value"] for d in spent_for]),
		"total_spent": self_exp
	}
	x = expense_collection.insert_one(input_doc)
	print(x.inserted_id)
	return True

def view_mem():
	while True:
		name = input("\nEnter member name :\n||:")
		if member_collection.find_one({"name": name}):
			break
		print("\nGiven name does not exist! Try again...\n")
	view_member(name)
	return True
def view_member(n):
    exps = expense_collection.find(
                    {"spent_by": n}
            )
    loans = expense_collection.find(
    {"spent_for.name": n},
    {"cause": 1, "spent_by": 1, "date": 1, "spent_for":
        {"$elemMatch": {"name": n}}
        }
    )
    e = []
    l = []
    index_exp = {"cause": [], "amount": []}
    for doc in exps:
        cause = doc["cause"]
        total = doc["total_spent"]
        self_exp = doc["self"]
        spent_for = [obj["name"] for obj in doc["spent_for"]]
        time = doc["date"]
        e.append([cause, total, spent_for, time])
        index_exp["cause"].append(cause)
        index_exp["amount"].append(self_exp)
    for doc in loans:
        cause = doc["cause"]
        spent_by = doc["spent_by"]
        value = doc["spent_for"][0]["value"]
        time = doc["date"]
        l.append([cause, spent_by, value, time])
        index_exp["cause"].append(cause)
        index_exp["amount"].append(value)
    #output
    print(n)
    for item in e + l:
    	print(item)
    print("\n")
    print(index_exp["cause"])
    print(index_exp["amount"])
    print("\nTotal: {}\n".format(sum(index_exp["amount"])))
    print("\n\n")

def update():
	member_list = member_collection.find(
                {"document": {"$ne": "default"}},
                {"_id": 0}
                )
	member_list = [doc["name"] for doc in member_list]
	for member in member_list:
		view_member(member)
	#print(list(member_list))
	return True


def transaction():
	while True:
		From = input("\nFrom ||: ")
		if member_collection.find_one({"name": From}):
			break
		print("\nGiven name doesn't exist! Try again...")
	while True:
		to = input("To ||: ")
		loans = expense_collection.find(
		    {"spent_by": to, "spent_for.name": From},
		    {"cause": 1, "spent_for": 
		        {"$elemMatch": {"name": From}}
		    }
		    )
		loans = list(loans)
		#print(loans)
		if not len(loans) == 0:
			break
		print("\nGiven name doesn't exist! Try again...\n")
	while True:
		cause = input("Cause ||: ")
		causes = [x["cause"] for x in loans]
		if cause in causes:
			break
		print("\nGiven Cause doesn't exist! Try again...\n")
	amount = input("Amount ||: ") #modification needed
	input_doc = {
		"_id": transaction_collection.count(),
		"from": From,
		"to": to,
		"cause": cause,
		"amount": int(amount),
		"date": str(datetime.datetime.now())
	}
	x = transaction_collection.insert_one(input_doc)
	print(x.inserted_id)
	return True


def relation():
	while True:
		name1, name2 = input("\nEnter name1 and name2 :\n||: ").split()
		e1 = bool(member_collection.find_one({"name": name1}))
		e2 = bool(member_collection.find_one({"name": name2}))
		if e1 and e2:
			break
		elif not (e1 or e2):
			err = name1 + " and " + name2
		elif not e1:
			err = name1
		else:
			err = name2
		print(err + " does not exist! Try again...\n")
	rel(name1, name2)
	return True
def rel(n1, n2):
	names = {"$in": [n1, n2]}
	rel_data = expense_collection.find(
	    {"$and": 
	        [{"spent_by": names},
	        {"spent_for.name": names}]
	    },
	    {"_id": 0, "cause": 1,"spent_by": 1,"date": 1, "spent_for": 
	        {"$elemMatch": {"name": names}}
	    }
	)
	rel_data = list(rel_data)
	for d in rel_data:
		#print("\nnew\n")
		a = d.pop("spent_for")[0]["value"]
		d["amount"] = int(a)
		sb = d.pop("spent_by")
		if not n1 == sb:
			d["amount"] *= (-1)
			#print("\n{} {}\n",n1, sb)
		tran = transaction_collection.find(
		    {"cause": d["cause"], "from": names},
		    {"_id": 0, "from":1, "amount": 1, "date": 1}
		)
		trans = list(tran)
		for t in trans:
			f = t.pop("from")
			if not n1 == f:
				t["amount"] *= (-1)
		d["transactions"] = trans
		d["balance"] = d["amount"] + sum([t["amount"] for t in trans])
	pprint(rel_data)
	final = sum([d["balance"] for d in rel_data])
	print("final balance", final)


commandSet = {"create": create, "end": end, "spend": spend, "update": update, "transact": transaction,
				"relation": relation, "view": view_mem}

def load_db():
	global expense_collection, member_collection, transaction_collection

	def insert_default_value(collection):
		now = str(datetime.datetime.now())
		collection.update_one(
			{"document": "default"},
	        {
	            "$setOnInsert": {"insertion_date": now},
	            "$set": {"last_update_date": now},
	        },
	        upsert=True)

	print("starting app...\n")
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	db = myclient["Expense_Manager"]

	expense_collection = db["Manager-1:Expenses"]
	member_collection = db["Manager-1:Members"]
	transaction_collection = db["Manager-1:Transactions"]
	insert_default_value(expense_collection)
	insert_default_value(member_collection)
	insert_default_value(transaction_collection)

	member_collection.create_index([("name", 1)])
	expense_collection.create_index([("cause", 1), ("spent_by", 1), ("spent_for.name", 1)])

	dblist = myclient.list_database_names()
	if "Expense_Manager" in dblist:
		print("Database loaded...!\n")
	else:
		raise NameError("Database failed to load.")


def main():
	# load database
	load_db()

	loop = True
	while loop:
		command = input("\n==> ")
		if not command in commandSet.keys():
			print("Wrong Command! Try again...\n")
			continue
		loop = commandSet[command]()

if __name__ == "__main__":
	main()


#  --*--  #