def find_cliques(graph):
    
    def bronk(R, P, X):
        
        if not P and not X:
            yield R
            return
        
        for v in list(P):
            neighbors = {n for n, connected in graph[v].items() if connected and n != v}            
            yield from bronk(R | {v}, P & neighbors, X & neighbors)
            P.remove(v)
            X.add(v)

    nodes = set(graph.keys())
    return list(bronk(set(), nodes, set()))