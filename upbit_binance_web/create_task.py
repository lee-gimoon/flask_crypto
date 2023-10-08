import asyncio

async def my_coroutine():
    print("Coroutine started!")
    await asyncio.sleep(1)
    print("Coroutine finished!")

async def main():
    print("Before task creation")
    task = asyncio.create_task(my_coroutine()) # asyncio.create_task() 함수는 주어진 코루틴을 즉시 스케줄링하고, 이 코루틴의 실행을 나타내는 asyncio.Task 객체를 반환합니다.
    print("After task creation")
    await asyncio.sleep(2)  # This sleep ensures we see the coroutine's output
    print("After sleep in main")

asyncio.run(main())

# 이 출력을 통해 asyncio.create_task() 호출 직후에 "After task creation"이 출력되고, 그 다음에 코루틴의 "Coroutine started!"가 출력되는 것을 확인할 수 있습니다. 
# 이것은 asyncio.create_task()가 코루틴을 즉시 실행하지 않고 스케줄링만 한다는 것을 나타냅니다.