import asyncio
import time

from modules.transaction_router import APIWrapper


async def main():
    rpc_endpoint = "rpc.lettry.xyz"
    api_wrapper = APIWrapper(rpc_endpoint)
    await api_wrapper.subscribe_to_new_blocks()


if __name__ == "__main__":
    asyncio.run(main())
