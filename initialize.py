#This program will save your information for quicker catching
#The data will only save locally.

import json,re


def save_user_date(user_data:dict):
    with open("user_data.json",mode="w",encoding="utf-8") as file:
        json.dump(user_data,file,indent=2)

def main()->dict:
    user_data = {}
    user_data["std_id"] = input("Input your Student ID: ")
    user_data["password"] = input("Input your password: ")

    general_course_data={"a":[],"b":[]}
    while True:
        source=""
        course_data={}
        while source not in ["a","b","q"]:
            source = input("输入课程来源(a.方案选课/b.自由选课/q.停止添加)(输入a或b即可): ")
        if(source == "q"):
            break
        course_data["course_id"]=input("输入课程号: ")
        course_data["course_index"]=input("输入课序号(必须为两位数，如:01、33): ")
        try:
            int(course_data["course_id"]),int(course_data["course_index"])
            if len(course_data["course_index"]) != 2:
                raise Exception
        except:
            print("Invaild course!Failed to add the course!")
            continue
        general_course_data[source].append(course_data)

    user_data["course"]=general_course_data
    save_user_date(user_data)
    print("Done!")
    return user_data

def show_user_data(user_data:dict) -> None:
    print("User information:")
    print("Student ID:%s"%(user_data["std_id"]),"Password:%s"%(user_data["password"]),sep="\n")
    print("Your courses:")
    print("-"*20)
    print("Plan courses:")
    print("\n".join(map(lambda x:"Course %s_%s"%(x["course_id"],x["course_index"]),user_data["course"]["a"])))
    print("-"*20)
    print("Free courses:")
    print("\n".join(map(lambda x:"Course %s_%s"%(x["course_id"],x["course_index"]),user_data["course"]["b"])))
    print("-"*20)

def update(user_data:dict) -> dict:
    show_user_data(user_data)

    operate = ""
    while True:
        while operate not in ["i","p","a","b","q"]:
            operate = input("请输入更新指令(i.更改学号/p.更改密码/a.更改方案选课/b.更改自由选课/s.展示当前信息/q.保存并退出)(输入前面的字母即可):")
        if operate == "q":
            return user_data
        elif operate == "i":
            user_data["std_id"] = input("Input the new std_id:")
            print("Student ID has been updated!")
        elif operate == "p":
            new_passwd = input("Input the new password:")
            if new_passwd == input("Input the new password again:"):
                user_data["password"] = new_passwd
                print("Password has been updated!")
            else:
                print("The passwords entered did not match.Failed to update the password!")
        elif operate in ["a","b"]:
            order,args = "",[]
            name = "方案选课" if operate == "a" else "自由选课"
            en_name = "Plan courses" if operate == "a" else "Free courses"
            while True:
                print("%s:"%(en_name))
                print("\n".join(map(lambda x:"%d.%s"%(x[0],x[1]),enumerate(map(lambda x:"Course %s_%s"%(x["course_id"],x["course_index"]),user_data["course"][operate]),1))))
                while order not in ["a","d","q"]:
                    manage = input("请输入更改%s的指令(a [课程号] [课序号].添加新的课程/d [序号].删除第[序号]条课程/q.退出方案选课更新)(输入指令并带上参数):"%(name))
                    order = manage.split(" ")[0]
                    args = re.findall(r"\d+",manage)
                if order == "q":
                    break
                elif order == "a":
                    if len(args) == 2:
                        try:
                            numbers = [int(i) for i in args]
                            if len(args[1]) != 2:
                                raise Exception
                            new_course = {"course_id":args[0],"course_index":args[1]}
                            if not new_course in user_data["course"][operate]:
                                user_data["course"][operate].append(new_course)
                                print("Successfully added Course %s_%s!"%(args[0],args[1]))
                            else:
                                print("Course %s_%s has already existed!"%(args[0],args[1]))
                        except:
                            print("Invaild arguments type!Failed to add the course!")
                    else:
                        print("Invaild number of arguments!Failed to add the course!")
                elif order == "d":
                    if len(args) == 1:
                        try:
                            pos = int(args[0])
                            try:
                                if pos <= 0:
                                    raise Exception
                                target = user_data["course"][operate][pos-1]
                                del user_data["course"][operate][pos-1]
                                print("Successfully deleted the Course %s_%s!"%(target["course_id"],target["course_index"]))
                            except:
                                print("Invaild position!Failed to delete the course!")
                        except:
                            print("Invaild argument type!Failed to delete the course!")
                    else:
                        print("Invaild number of arguments!Failed to add the course!")
                order,args = "",[]
        elif operate == "s":
            show_user_data(user_data)
        operate = ""

if __name__ == "__main__":
    try:
        with open("user_data.json",mode="r") as file:
            new_json = update(json.load(file))
        save_user_date(new_json)
        print("Update finished!")
    except:
        main()

    