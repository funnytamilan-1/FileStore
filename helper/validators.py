def ids_range(start:int,end:int,max_items:int=1000)->list[int]:
    start,end=int(start),int(end)
    if start<=0 or end<=0: raise ValueError("message IDs must be positive")
    step=1 if end>=start else -1; values=list(range(start,end+step,step))
    if len(values)>max_items: raise ValueError("range is too large")
    return values
