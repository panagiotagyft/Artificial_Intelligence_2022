import re 
import csp
import time

class kenken(csp.CSP):

    def __init__(self, kenken_problem: str):

        # definition important structures of the csp problem
        self.Variables = []     # the coordinates of the boxes, i.e. the general form of coordinates is as follows -->> (row, column)
        self.Domains = {}       # the value domain for each variable, Di = [1,n] (n-->> the dimension of the grid).
        self.Neighbors = {}     # the neighbouring boxes

        # definition structures, which will have stored information about the cliques
        self.Cliques = {}
        self.CliqueOperations = {}

        self.kenken_size = 0    # the size of grid

        # extraction of problem data
        self.extractProblemData(kenken_problem)

        domainValues = [ item for item in range(1, self.kenken_size+1) ]     # domain creation
        
        self.Domains = { element: domainValues for element in self.Variables }        # initialize Domains

        # definition a structure that will have stored row and column neighbors for each variable
        neighbors_line_column = []

        # initialize Neighbors 
        for v in self.Variables:
            
            # initialize neighbors_line_column[]
            neighbors_line_column = [ element for element in self.Variables if (element is not v) if (element[0] == v[0]) or (element[1] == v[1])]
              
            self.Neighbors[v] = neighbors_line_column

        csp.CSP.__init__(self, self.Variables, self.Domains, self.Neighbors, self.kenken_constraint)

    def kenken_constraint(self,A,a,B,b):

        # 1. Check for non-display restriction violation same number in the same row and column! 
        if A in self.Neighbors[B]:
            if a == b: return False
        
        # 2. Control violation of the constraint of the numerical result of the clique!
        #  first find the clique to which the squares belong
        for clique in self.Cliques.keys():
            if A in self.Cliques[clique] and B in self.Cliques[clique]:   # The two squares belong to the same clique.
                return self.clique_constraint(A, a, B, b, clique)
            if A in self.Cliques[clique]:
                conA = self.clique_constraint(A, a, A, a, clique)
            if B in self.Cliques[clique]:
                conB = self.clique_constraint(B, b, B, b, clique)

        if conA == True and conB == True: 
            return True

        return False


    def clique_constraint(self, A, a, B, b, clique):
        
        
        # Stores all squares of the clique assigned a value.
        auxilaryDict = { var: self.infer_assignment()[var] for var in self.Cliques[clique] if var in self.infer_assignment() }
 
        # If there are no the squares A and B in the dictionary they are also stored.
        if A not in auxilaryDict.keys() and B not in auxilaryDict.keys():
            auxilaryDict[A] = a 
            auxilaryDict[B] = b

        # Export information of numerical result  and numeric action symbol.
        regural_expr ='\d+'
        res = re.findall(regural_expr, self.CliqueOperations[clique])
        res = res[0]
 
        operation = self.CliqueOperations[clique]
        operation = operation.replace(res, '')
        res = int(res)
  

        if len(self.Cliques[clique]) == 1:          # The value of the square matches the target value?
            if res == a and a == b and A == B: 
                return True
            
        elif operation == '+':    # Calculation of sum.
            addition = sum( auxilaryDict[var] for var in auxilaryDict.keys() )
            if addition <= res : return True

        elif operation == '-':
           
            # If we have one square.
            if a == b and A == B:
                # Find the second box of the clique.
                for element in self.Cliques[clique]:
                    if element is not A:
                        break
                # If no value is assigned to one of the two boxes contained in the clique -- then -->> find the appropriate assignment 
                # for this box.
                if len(auxilaryDict) == 1:
                    for item in self.domains[element]:
                        if abs(item-a) == res: return True
                else:
                    if abs(auxilaryDict[element] - a) == res: return True
            else:
                if abs(a - b) == res: return True

        elif operation == '*':    # Calculation of product.
            multiplication = 1
            for var in auxilaryDict.keys():
                multiplication *= auxilaryDict[var]

            if multiplication == res and (len(auxilaryDict) == len(self.Cliques[clique])): return True
            elif multiplication <= res and (len(auxilaryDict) < len(self.Cliques[clique])):  return  True

        elif operation == '/':
            
            # If we have one square.
            if a == b and A == B:
                # Find the second box of the clique.
                for element in self.Cliques[clique]:
                    if element is not A:
                        break
                # If no value is assigned to one of the two boxes contained in the clique -- then -->> find the appropriate assignment 
                # for this box.
                if len(auxilaryDict) == 1:
                    for item in self.domains[element]:
                                    
                        division1 = item/a
                        division2 = a/item
                        
                        if division1 == res: return True
                        elif division2 == res: return True

                else:
                    division1 = auxilaryDict[element]/a
                    division2 = a/auxilaryDict[element]
                        
                    if division1 == res: return True
                    elif division2 == res: return True
            else:
                division1 = a/b
                division2 = b/a
                    
                if division1 == res: return True
                elif division2 == res: return True
        
        return False

    
    def extractProblemData(self, kenken_problem: str):
        """
        Extract information from the encoded representation of the problem.
        """

        # auxiliary variables to extract the problem data!
        flag_line = False
        flag_column = False
        flag_clique = False
        flag_operation = False

        counter_dot = 0

        operation = ""
        clique_name = ""
        tup = ()

       # extraction of problem data
        for char in kenken_problem:
            
            if char == 'l':     # go to the next line
                self.kenken_size += 1       # counter of the distance of grid
                counter_dot = 0
                flag_line = True
                continue
            elif flag_line == True:
                x = int(char)
                flag_line = False
                continue
            elif char == 'c':   # go to the next column
                flag_column = True
                continue
            elif flag_column == True:
                y = int(char)
                # x: row, y:column
                tup = (x,y)  
                self.Variables.append(tup)
                flag_column = False
                continue
            elif char == '_':  
                flag_clique = True
                continue
            elif flag_clique == True:
                
                if char in self.Cliques.keys():
                    auxiliaryList = [ item for item in self.Cliques[char] ]
                else:
                    auxiliaryList = []

                auxiliaryList.append(tup)
                self.Cliques[char] = auxiliaryList
                
                flag_clique = False
                
                continue
            elif char == '.': 
                counter_dot += 1
                continue
            elif counter_dot == 3:   #  info about cliques and operations

                if char == ',':     # go to the next clique
                    flag_operation = False
                    self.CliqueOperations[clique_name] = operation
                    clique_name = ""
                    operation = ""
                    continue
                elif char == ':':
                    flag_operation = True
                    continue
                elif flag_operation == True:    # save operation
                    operation += char 
                    continue
                else:
                    clique_name += char     # save clique's name

            else: 
                continue

        self.CliqueOperations[clique_name] = operation


    def display(self, assignment):
        
        size = self.kenken_size

        if len(assignment) == 0:
            print("Error!")
        char =""
        print("+", end="")
        for i in range(1, size+1): char += "----+"
        print(char)
        
        for i in range(1, size+1): 
            char1 = "| "
            print(char1, end="")
            for j in range(1, size+1):
                print(assignment[(i,j)], end="  | ")
            print("")
            print("+"+char)
        
        print("\n-- Info: Operations --\n")
        for i in range(1, size+1): 
            for j in range(1, size+1):
                for l in self.Cliques.keys():
                    if self.Cliques[l][0] == (i,j):
                        print(f"position: {self.Cliques[l][0]}   operation: {self.CliqueOperations[l]}")


if __name__ == "__main__":
    
    print("\n\n- Choose a puzzle from the following:")
    print(" -- Puzzles  --")
    print("1. 3x3\n2. 4x4\n3. 5x5\n4. 6x6\n5. 7x7\n")
    
    Puzzle = input("type the puzzle you want: ")

    print("\n\n- Select an algorithm from the following:")
    print(" -- Algorithms  --")
    print("1. BT\n2. BT+MRV\n3. FC\n4. FC+MRV\n5. MAC\n6. MinConflicts\n")

    Algorithm = input("type the algorithm you want: ")

    print("\n")

    start = time.time()
    
    if Puzzle == "3x3":
        test = "l1c1_A,c2_B,c3_C.l2c1_A,c2_B,c3_B.l3c1_D,c2_D,c3_D...A:2/,B:8+,C:1,D:6*"
    
    if Puzzle == "4x4":
        test = "l1c1_A,c2_B,c3_C,c4_C.l2c1_D,c2_D,c3_E,c4_C.l3c1_F,c2_F,c3_E,c4_E.l4c1_G,c2_G,c3_H,c4_I...A:4,B:2,C:9*,D:2/,E:8*,F:3*,G:2-,H:4,I:2"
    
    if Puzzle == "5x5":
        test = "l1c1_A,c2_A,c3_B,c4_C,c5_C.l2c1_D,c2_D,c3_B,c4_E,c5_F.l3c1_G,c2_H,c3_I,c4_E,c5_F.l4c1_G,c2_H,c3_I,c4_J,c5_F.l5c1_K,c2_K,c3_L,c4_M,c5_M...A:4-,B:1-,C:2/,D:3-,E:4-,F:60*,G:4+,H:2/,I:2/,J:3,K:1-,L:5,M:2/"
    
    if Puzzle == "6x6":
        test = "l1c1_A,c2_B,c3_B,c4_C,c5_C,c6_C.l2c1_A,c2_D,c3_E,c4_E,c5_C,c6_C.l3c1_F,c2_D,c3_G,c4_G,c5_H,c6_I.l4c1_F,c2_F,c3_J,c4_J,c5_H,c6_I.l5c1_K,c2_L,c3_M,c4_M,c5_N,c6_N.l6c1_K,c2_L,c3_L,c4_O,c5_O,c6_N...A:3-,B:4-,C:72*,D:6*,E:9+,F:8+,G:4-,H:3-,I:1-,J:3/,K:5-,L:10+,M:2/,N:10+,O:2/"
    
    if Puzzle == "7x7":
        test = "l1c1_A,c2_A,c3_B,c4_B,c5_C,c6_C,c7_D.l2c1_E,c2_F,c3_G,c4_G,c5_G,c6_H,c7_D.l3c1_E,c2_F,c3_I,c4_I,c5_J,c6_K,c7_K.l4c1_L,c2_L,c3_M,c4_M,c5_J,c6_N,c7_O.l5c1_P,c2_Q,c3_R,c4_S,c5_S,c6_N,c7_O.l6c1_P,c2_T,c3_R,c4_U,c5_V,c6_N,c7_W.l7c1_P,c2_T,c3_X,c4_X,c5_V,c6_W,c7_W...A:28*,B:1-,C:1-,D:4-,E:2/,F:10+,G:10+,H:4,I:6-,J:1-,K:3-,L:3-,M:12*,N:6+,O:13+,P:10+,Q:6,R:2-,S:3-,T:6+,U:6,V:2/,W:14+,X:3-"
    

    ken = kenken(test)

    if Algorithm == "BT": 
        assignment = csp.backtracking_search(ken)
    
    if Algorithm == "BT+MRV": 
        assignment = csp.backtracking_search(ken, select_unassigned_variable=csp.mrv)
    
    if Algorithm == "FC": 
        assignment = csp.backtracking_search(ken, inference=csp.forward_checking)
    
    if Algorithm == "FC+MRV": 
        assignment = csp.backtracking_search(ken, select_unassigned_variable=csp.mrv, inference=csp.forward_checking)
    
    if Algorithm == "MAC": 
        assignment = csp.backtracking_search(ken, inference=csp.mac)

    if Algorithm == "MinConflicts":
        assignment = csp.min_conflicts(ken)

   

    end = time.time()
    total_time = end - start
    print("The total time is:", total_time)

    print("Number of assignments:", ken.nassigns)
    
    ken.display(assignment)