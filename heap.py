

#each node is a tuple of (docID, cos-score)
class heap:
    def __init__(self):
        self.lst = [0]
        self.curr_size = 0

    def shiftup(self, curr_heap_size):
        while curr_heap_size//2 > 0:
            curr_tup_node = self.lst[curr_heap_size]
            parent_tup_node = self.lst[curr_heap_size//2]
            #if cosine score of curr node > cosine score of parent node, then swap the two
            if curr_tup_node[1] > parent_tup_node[1]:

                self.lst[curr_heap_size//2] = curr_tup_node
                self.lst[curr_heap_size] = parent_tup_node
            curr_heap_size = curr_heap_size //2 

    #insert a node (underlying structure is a tuple) into the heap
    def insert(self, tup_node):
        self.lst.append(tup_node)
        self.curr_size += 1
        self.shiftup(self.curr_size)

    #get max(right_child, left_child)
    def get_max_child(self, i):
        if i * 2 + 1 > self.curr_size:
            return i * 2
        
        #left child
        left_tup_node = self.lst[i * 2]
        #right child
        right_tup_node = self.lst[i * 2 + 1]
        #if cos-score of right child is more than left child, than return index of right child
        if right_tup_node[1] > left_tup_node[1]:
            return i * 2 + 1
        #else, return index of left child
        return i * 2
    
    def shiftdown(self, i):
        while (i * 2) <= self.curr_size:
            #get index of max_child
            index_max_child = self.get_max_child(i)
            curr_tup_node = self.lst[i]
            max_child_tup_node = self.lst[index_max_child]

            if curr_tup_node[1] < max_child_tup_node[1]:
                tmp = max_child_tup_node
                #replace max child with curr child
                self.lst[index_max_child] = curr_tup_node
                #replace curr_child with max child
                self.lst[i] = tmp
            #repeat the loop with i == index of max child
            i = index_max_child

    def remove_max(self):
        #get the max node, which is a tuple of (docID, cos-score)
        max_node = self.lst[1]
        #replace top element with last element of the list
        self.lst[1] = self.lst[self.curr_size]
        #decrease heap size since we remove top node
        self.curr_size = self.curr_size - 1
        #remove last element of list since we replace top node with last element and it's redundant
        self.lst.pop()
        self.shiftdown(1)
        return max_node
    
    #accepts a list of tuples in the form of [ (docID, cos-score), .... ]
    def build_heap(self, dic):
        self.curr_size = len(dic)
        for docID in dic:
            curr_tup = (docID, dic[docID])
            self.lst.append(curr_tup)
        i = len(dic) // 2
        while i > 0 :
            self.shiftdown(i)
            i -= 1


