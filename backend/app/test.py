from crypto import cryptofunctions
from model import structures
from opcua.gdsInterface import open62541GDS
from asyncua import Client
import asyncio

async def test():
    gds_url = "opc.tcp://localhost:4840"
    client = Client(gds_url)
    await client.connect()

    gds_interface = open62541GDS(client,
                                structures.NodeId(3, 5005),
                                structures.NodeId(2, 141),
                                structures.NodeId(3, 5004),
                                structures.NodeId(3, 7020),
                                structures.NodeId(3, 7011),
                                structures.NodeId(2, 204),
                                structures.NodeId(3, 7019),
                                structures.NodeId(3, 7010),
                                structures.NodeId(3, 7014),
                                structures.NodeId(3, 7009)
                                )

    trustlist_nodeId = structures.NodeId(2, 50076)
    trustlist = await gds_interface.readTrustList(trustlist_nodeId)
    #parsed_list = cryptofunctions.bytes_2_trustlist(trustlist)
    #print(trustlist)

if __name__ == "__main__":
    asyncio.run(
        test()
    )
