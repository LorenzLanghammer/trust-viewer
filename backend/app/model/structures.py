from asyncua import Client, common, ua

class NodeId():
    def __init__(self, namespace, id):
        self.namespace = namespace
        self.id = id
    
    def __repr__(self):
        return f"(namespace: {self.namespace}, id: {self.id})"
    
    def __eq__(self, other):
        if not hasattr(other, "namespace") or not hasattr(other, "id"):
            return False
        return (self.namespace, self.id) == (other.namespace, other.id)

    def __hash__(self):
        return hash((self.namespace, self.id))

def nodeid_2_uaNode(x: NodeId, client: Client) -> common.Node:
    return client.get_node(ua.NodeId(x.id, x.namespace))

def nodeid_2_uaNodeId(x: NodeId) -> ua.NodeId:
    return ua.NodeId(x.id, x.namespace)

def uaNodeId_2_nodeid(x: ua.NodeId) -> NodeId:
    return NodeId(x.NamespaceIndex, x.Identifier)
