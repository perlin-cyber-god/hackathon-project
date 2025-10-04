student = {
    "Name" : "Hitarth",
    "Subject" : {
        "Phy" : 90,
        "Chem" : 52,
        "Math" : 35
    }
}
print(student["Subject"])
print(student["Subject"]["Phy"])
print(student.keys())
#to convert them into key we can cast it like we useed to with int
print(list(student.keys())) #len(student) se no of keys find kar sakte hai
print(student.values())
print(student.items())
pair = list(student.items())
print(pair[1])
print(student.get("Name"))
newdict= {"City" : "Ahmedabad",
          "Age" : "18"}
student.update(newdict)
print(student)