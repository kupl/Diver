import os,sys
import shutil
from termcolor import colored
from parser.smt_parser import *

let_bind = {}
define_bind = {}

def refresh_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
        os.mkdir(dir_path)

def get_name(file):
    name = file.split('/')[-1]
    return name


def create_core_dir(res_dir,server,core,solver=None):
    server_dir = os.path.join(res_dir,server)
    core_dir = os.path.join(server_dir,"core_"+str(core))
    if solver is not None:
        solver_dir = os.path.join(core_dir,solver)
        os.makedirs(solver_dir,exist_ok=True)
    else:
        os.makedirs(core_dir,exist_ok=True)
    return core_dir


def create_dir(path_dir):
    if solver is not None:
        solver_dir = os.path.join(path_dir,solver)
        os.makedirs(solver_dir,exist_ok=True)
    else:
        os.makedirs(path_dir,exist_ok=True)

    return path_dir

    
def create_bug_dir(dir):
    os.makedirs(dir,exist_ok=True)
    return dir

def get_seed_files(path_to_dir):
    file_paths = list()

    if ".smt2" in path_to_dir:
        return [os.path.abspath(path_to_dir)]

    for r, d, f in os.walk(path_to_dir):
        for file in f:
            if ".smt20" in file:
                continue
            if ".smt2" in file:
                file_paths.append(os.path.join(r,file))
    return file_paths

def get_variable(seed_file):
    try:
        f = open(seed_file,"r",encoding='utf-8')
        lines = f.read().splitlines() #'\n' 기준으로 저장
        f.close()
        f = open(seed_file,"w",encoding='utf-8')
        cmd = ['check-sat','set-logic','echo','exit','get-assertions','get-info','get-model','get-option','get-proof','get-unsat-assumptions','get-unsat-core','pop','push','reset','reset-assertions','set-info','set-logic','set-option','declare-fun','declare-const','define-fun','get-value','maximize','minimize']
        model_state = False

        prev = 0
        for line in lines:
            if line =="" or line[0]==';':
                prev+=1
                continue
            f.write(line)
            prev+=1
            break

        for idx in range(prev,len(lines)):
            line = lines[idx]
            if line =="" or line[0]==';':
                continue
            if "get-model" in line:
                model_state = True

            if "exit" in line:
                if model_state == False:
                    f.write("\n(get-model)")
                f.write('\n'+line)
                continue
            
            l = [t_ in line for t_ in cmd] 
            if 1 in l:
                f.write("\n"+line)
            elif "assert" in line:
                f.write("\n"+line)
            else:
                new_line = line.split()
                stmt = ""
                for t in new_line:
                    if t=="":
                        continue
                    stmt = stmt+" "+t
                f.write(stmt)
        f.close()

        f = open(seed_file,"r",encoding='utf-8')
        lines = f.read().splitlines()
        f.close()
        f = open(seed_file,"w",encoding='utf-8')

        logic = None
        for line in lines:
            sub_line = line.split(" ")
            if sub_line[0]=="(set-logic":
                f.write(line+"\n")
                logic = sub_line[1][:-1]
                if "RA" in line:
                    f.write("(set-option :pp.decimal true)\n")
                continue
            elif sub_line[0]=="(set-info":
                continue
            elif "(set-option :pp.decimal true)" in line:
                continue
            f.write(line+"\n")
        f.close()

        var={}
        brackets="()"
        var_type=["Real","Int","Bool","String"]
        f = open(seed_file,"r",encoding='utf-8')
        lines = f.read().splitlines()

        idx = 0 
        declare_line = {}

        for line in lines:
            if "declare-" in line:
                line = ''.join(x for x in line if x not in brackets)
                l=line.split()
                var_t = list(set(l)&set(var_type))
                if var_t == []:
                    print(colored("{} type is not provided.".format(l[2]),"red","on_white"))
                    continue
                var[l[1]]=var_t[0]
            elif "define-fun" in line:
                line = ''.join(x for x in line if x not in brackets)
                l=line.split()
                var_t = list(set(l)&set(var_type))
                if var_t == []:
                    print(colored("{} type is not provided.".format(l[1]),"red","on_white"))
                    continue
                var[l[1]]=var_t[0]
            if "(assert" in line:
                declare_line[idx]=var.copy()

            if "get-model" in line:
                model_state = True

            idx+=1
        return var,declare_line,logic

    except Exception as e:
        print(colored("{} Exception while read orig smt file".format(seed_file), "red", "on_white"))
        return None,None




def let_remove(node):
    global let_bind 
    global define_bind
    node_name = node.__class__.__name__
    if node_name == "Variable":
        if node[0] in list(let_bind.keys()):
            node_stmt = let_bind[node[0]]
        elif node[0] in list(define_bind.keys()):
            node_stmt = define_bind[node[0]]
        else:
            node_stmt = node[0]
    elif node_name in ["Constant","Bool","Const_String","RegLan"]:
        node_stmt = node[0]
    elif node_name == "Letstmt":
        node_stmt = ""
        _ = let_remove(node[2])
        for idx in range(3,len(node)-1):
            if node[idx].__class__.__name__ =="Letstmt":
                node_stmt = node_stmt+let_remove(node[idx])
            else:
                node_stmt = node_stmt+" "+let_remove(node[idx])
    elif node_name == "Bind_List":
        var = []
        formula_a = []
        for i in range(2,len(node)-1):
            if node[i].__class__.__name__=="str":
                continue
            if node[i].__class__.__name__=="Bind_Var":
                var.append(node[i][0])
            else:
                formula_a.append(let_remove(node[i]))
        for i in range(len(var)):
            let_bind[var[i]] = formula_a[i]
        node_stmt = ""
    else:
        node_stmt = "("+node[1]
        for idx in range(2,len(node)-1):
            node_stmt = node_stmt+" "+let_remove(node[idx])
        node_stmt+=")"
    return node_stmt


def optimize_smt2(smt2):
    global let_bind 
    global define_bind

    let_bind.clear()
    define_bind.clear()
    let_ast = transform_smt_to_ast(smt2)
    f = open(smt2,"w",encoding='utf-8')
    #set-logic --> 뒤에 오기
    assert_queue = []
    #define_bind = {}
    cid = 0

    for cmd in let_ast:
        if not(cmd[1] in ["set-logic","define-fun","declare-fun","assert",
                        "check-sat","get-model","declare-const"]):
            continue
        if cmd[1]== "assert":
            assert_queue.append(cmd)
            continue
        elif cmd[1]=="define-fun":
            new_cmd = cmd[0]
            fun_name = cmd[2]
            for idx in range(1,len(cmd)-1):
                if cmd[idx].__class__.__name__ != "str":
                    let_bind.clear()
                    cmd[idx] = let_remove(cmd[idx])
                    define_bind[fun_name] = cmd[idx]
                if cmd[idx-1] == "(":
                    new_cmd = new_cmd+cmd[idx]
                else:
                    new_cmd = new_cmd+" "+cmd[idx]
            new_cmd += ")"
        elif cmd[1]=="check-sat":
            break
        else:
            new_cmd = cmd[0]
            for idx in range(1,len(cmd)-1):
                if cmd[idx].__class__.__name__ != "str":
                    let_bind.clear()
                    cmd[idx] = let_remove(cmd[idx])
                if cmd[idx-1] == "(":
                    new_cmd = new_cmd+cmd[idx]
                else:
                    new_cmd = new_cmd+" "+cmd[idx]
            new_cmd += ")"
        f.write(new_cmd+"\n")
    for ass in assert_queue:
        let_bind.clear()
        remove_let = let_remove(ass[2])
        new_cmd = "(assert "+remove_let+")"
        f.write(new_cmd+"\n")

    f.write("(check-sat)\n")
    f.write("(get-model)")
    f.close()
    return


def bug_copy(seed_formula, mutant_formula, path, solver, SEED, org_path, bug_type, message = ""):
    now = time.localtime()
    t_format =  "%04d/%02d/%02d %02d:%02d:%02d"%(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    logging.debug("[{}] Seed Formula : {} ")

    bug_dir = os.path.join(os.getcwd(),"bug")
    bug_dir = os.path.join(bug_dir, solver)
    bug_dir = os.path.join(bug_dir, seed_formula+"_"+str(SEED))
    create_bug_dir(bug_dir)

    mutant = os.path.join(path, mutant_formula)
    shutil.copy2(org_path, bug_dir)
    shutil.move(mutant, bug_dir)

    if len(message)!=0:
        f = open(bug_dir+"/"+mutant_formula, mode = 'a', encoding = 'utf-8')
        f.write(";;"+message)
        f.close()
    return

def get_score(constraints, solver, model = None):
    nodes = list(constraints.keys())
    score = {}
    sum_score = 0.0

    for n in nodes:
        constraint = constraints[n][0]
        ty = constraints[n][1]
        s = 0.001
        if ty == "Bool":
            if constraint == [True,False]:
                s = 1.0
            else:
                s = 0.5
        elif ty == "Real" and "Int":
            if solver == "z3":
                l = constraint["l"]
                u = constraint["u"]
                l_class = l.__class__.__name__
                u_class = u.__class__.__name__
                if (l_class == "float" and l in [-inf,inf]) or (u_class == "float" and u in [-inf,inf]):
                    s = 1.0
                else:
                    res = simplify(u-l)
                    if is_algebraic_value(res):
                        tmp = float(str(res)[:-1])
                        if tmp >= 1000.0:
                            s = 1.0
                        else:
                            s = (int(tmp)+1.0)/1000.0
                    else:
                        s = (int(str(res))+1.0)/1000.0
            elif solver == "cvc":
                l = constraint["l"]
                u = constraint["u"]
                l_class = l.__class__.__name__
                u_class = u.__class__.__name__

                if (l_class == "float" and l in [-inf,inf]) or (u_class == "float" and u in [-inf,inf]):
                    s = 1.0
                else:
                    tmp = model.getValue(model.mkTerm(Kind.SUB, u,l))
                pass
            else:
                pass
        elif ty == "String":
            pass
        else: 
            pass
        sum_score += s
        score[n] = s


    return 