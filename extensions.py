from flask_sqlalchemy import SQLAlchemy;
import json

db = SQLAlchemy()

class GMCP:
    IAC = b"\xff"
    DO  = b"\xfd"
    SB  = b"\xfa"
    WILL = b"\xfb"
    SE  = b"\xf0"
    GMCP = b"\xc9"
    
    @staticmethod
    async def gmcp_order(writer):
        writer.write(GMCP.IAC + GMCP.DO + GMCP.GMCP) #for some reason icesus did not negotiate with WILL but do.
        await writer.drain()

        modules = [
            "Room.Info 1",
            "Party 1",
            "Party.Info 1"
        ]
        writer.write(
            GMCP.IAC + GMCP.SB + GMCP.GMCP +
            b"Core.Supports.Set " +
            json.dumps(modules).encode() +
            GMCP.IAC + GMCP.SE
        )
        await writer.drain()
        