import heapq

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0
    
    def push(self, item: str, priority: int):
        """
            This method push the item if there is not an element into priority queue with the same item and priority 
        """

        item_exists = False 
        
        # Check if priority queue contains the item with the same priority
        for i in range( len(self.heap) ):    
            
            # If there is an element into priority queue with the same item and priority as the element 
            # the user wants to insert   -- then -->>  don't add the item
            if item == self.heap[i][1] and priority == self.heap[i][0]:
                item_exists = True 
                print('The item already exists into priority queue.There will be no second registration!')          # optional
                break 
            else:  
                continue
        
        # If the item does not exist   -- then -->>  push the item 
        if item_exists == False:
            heapq.heappush(self.heap, (priority, item))            
            self.count += 1         # increase the counter

    
    def pop(self) -> str:
        """
            If priority queue is not empty then remove and return the smallest item
        """

        # Check if priority queue is empty
        # If priority queue is not empty   -- then -->>   remove the smallest item from the heap
        if self.isEmpty() == False :
            item = heapq.heappop(self.heap)[1]
            self.count -= 1         # decrease the counter
        else:
            item = "The queue is empty.Cannot complete this action!"            # optional
        
        return item         # return the smallest item
    

    def isEmpty(self) -> bool:
        """
            Returns if the PriorityQueue is empty.
            Returns a boolean value:   True -> empty pq   --or--  False -> not empty pq
        """
        if self.count == 0:
            return True
        else:
            return False     
    

    def update(self, item: int, priority: int):
        """
           This method updates the priority queue with the element passed by the user as an argument. 
        """
        item_exists = False 
        counter_1 = 0

        # Check if priority queue contains the item
        for i in range( len(self.heap) ):    

            if item in self.heap[i]:
                item_exists =True 
                counter_1 += 1          # counts the number of item in priority queue
                
                # check if the existing item in the priority queue has a 
                # higher priority than the examination priority
                if self.heap[i][0] > priority:  
                    
                    temp1 = list(self.heap[i])  # Tuples are immutable. To modify the tuple we'll convert the tuple into a list
                    temp1[0] = priority         # update the priority

                    self.heap.pop(i)            # remove current element from priority queue

                    temp2 = tuple(temp1)        # convert list to tuple 
                    
                    self.heap.insert(i, temp2)  # insert the updated element in heap 
                    

        # if priority queue contains the item and there are duplicate registrations
        # -- then -->> delete them
        if item_exists == True and counter_1 > 1:
            
            # initializing lists
            list1 = self.heap
            list2 = []

            # find the duplicate registrations and delete them
            for x in range( len(list1) ):
                counter_2 = 0           # counts duplicate registrations
                
                if list1[x][1] == item and list1[x][0] == priority:
                    if len(list2) == 0 :
                        list2.append(list1[x])
                    else:
                        # count duplicate registrations
                        for y in range( len(list2) ):
                            if  list1[x][0] == list2[y][0] and list1[x][1] == list2[y][1]:
                                counter_2 += 1 
                        
                        # If the item does not exist in list2  -- then -->> copy it to the list
                        if counter_2 == 0 :
                            list2.append(list1[x])
                else:
                     list2.append(list1[x])
                     
                    
            
            # update the heap 
            self.heap = list(list2)
            self.count = len(self.heap)
        

        # If the item does not exist   -- then -->>  push the item 
        if item_exists == False:
            heapq.heappush(self.heap, (priority, item))            
            self.count += 1         # increase the counter

    # optional
    def printPriorityQueue(self):
        print("\n")
        print(f"* Priority Queue (priority, item): {self.heap}\n ")
        print("\n")

def PQSort(List:list) -> list:
    """
        PQSort() sorts the items of a list by using the priority queue
    """
    pq = PriorityQueue()            # Create priority queue

    [pq.push(element, element) for element in List]     # add all elements into priority queue

    List.clear()    
    temp = len(pq.heap)         # number of repetitions
    List = [ pq.pop() for i in range(temp) ]            # fill list... but this time with sorted items

    return List

if __name__ == "__main__":

    #------------------------------   Test 1   ------------------------------
    print("\n\n")
    print("---  Test 1   --- ")

    q = PriorityQueue()         # Create priority queue

    print("\n")

    print("-- Insert element. Info: item -> task0 , priotity -> 0")
    q.push("task0", 0)
    print("\n")

    print("-- Insert element. Info: item -> task1 , priotity -> 0")
    q.push("task1", 0)
    print("\n")

    print("-- Insert element. Info: item -> task2 , priotity -> 5")
    q.push("task2", 5)
    print("\n")

    print("-- Insert element. Info: item -> task0 , priotity -> 1")
    q.push("task0", 1)
    print("\n")

    print("-- Insert element. Info: item -> task3 , priotity -> 1")
    q.push("task3", 1)
    print("\n")
    
    print("-- Insert element. Info: item -> task4 , priotity -> 2")
    q.push("task4", 2)
    print("\n")
    
    print("-- Insert element. Info: item -> task0 , priotity -> 0")
    q.push("task0", 0)
    print("\n")

    print("-- Insert element. Info: item -> task1 , priotity -> 3")
    q.push("task1", 3)
    print("\n")

    print("-- Insert element. Info: item -> task1 , priotity -> 1")
    q.push("task1", 1)
    print("\n")

    print("-- Insert element. Info: item -> task2 , priotity -> 5")
    q.push("task2", 5)
    print("\n")

    print("-- Insert element. Info: item -> task0 , priotity -> 3")
    q.push("task0", 3)
    
    q.printPriorityQueue()

    print("-- Update element. Info: item -> task0 , priotity -> 1")
    q.update("task0", 1)
    q.printPriorityQueue()

    print("-- Update element. Info: item -> task4 , priotity -> 0")
    q.update("task4", 0)
    q.printPriorityQueue()

    print("-- Update element. Info: item -> task0 , priotity -> 0")
    q.update("task0", 0)
    q.printPriorityQueue()

    print("-- Update element. Info: item -> task8 , priotity -> 10")
    q.update("task8", 10)
    q.printPriorityQueue()

    for i in range(len(q.heap)):
        print("-- Remove smallest element")
        t=q.pop()
        print(f"Removing element: {t}")
        q.printPriorityQueue()

    print("-- Remove smallest element")
    t=q.pop()
    print(f"Removing element: {t} \n\n\n")

    print("             -----  Sort the items of List  -----\n")

    List = [49, 7 , 19, 8, 4, 27, 94, 1, 38, 5, 22, 16, 50, 68, 100]
    print(f"List: {List}")
    
    List = PQSort(List)
    print(f"Sorted List: {List}\n\n\n")
 
#------------------------------   Test 2   ------------------------------

    print("---  Test 2   --- \n\n")
    
    q0 = PriorityQueue()         # Create priority queue
    
    print("-- Insert element. Info: item -> task1 , priotity -> 1")
    q0.push("task1", 1)
    print("-- Insert element. Info: item -> task1 , priotity -> 2")
    q0.push("task1", 2)
    print("-- Insert element. Info: item -> task0 , priotity -> 0")
    q0.push("task0", 0)

    q0.printPriorityQueue()

    print("-- Remove smallest element")
    t=q0.pop()
    print(f"Removing element: {t}\n")

    print("-- Remove smallest element")
    t=q0.pop()
    print(f"Removing element: {t}\n")

    print("-- Insert element. Info: item -> task3 , priotity -> 3")
    q0.push("task3", 3)
    print("-- Insert element. Info: item -> task3 , priotity -> 4")
    q0.push("task3", 4)
    print("-- Insert element. Info: item -> task2 , priotity -> 0\n")
    q0.push("task2", 0)

    print("-- Remove smallest element")
    t=q0.pop()
    print(f"Removing element: {t}")

    q0.printPriorityQueue()