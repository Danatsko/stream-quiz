import asyncio

from arq.worker import create_worker

from app.arq_worker import WorkerSettings


async def main() -> None:
    worker = create_worker(WorkerSettings)
    await worker.main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped by user")
