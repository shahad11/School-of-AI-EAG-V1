import asyncio
import time

async def adder(a, b):
        a+=10
        b+=20
        await asyncio.sleep(2)
        print("added more values to a and b")
        return a + b
async def waiter():
        await asyncio.sleep(1)
        print("waited for 1 second")
a = -10
b= - 20

async def main():
    await asyncio.gather(
        adder(a, b),
        waiter()
    )
if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    total = time.time() - start_time
    print(f"Total execution time: {total:.2f} seconds")



