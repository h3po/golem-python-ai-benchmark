#!/usr/bin/env python3
import argparse
import asyncio
from datetime import datetime, timedelta
import math
from pathlib import Path
import sys
from tempfile import gettempdir
from typing import AsyncIterable, List, Optional

from yapapi import Golem, NoPaymentAccountError, Task, WorkContext, windows_event_loop_fix
from yapapi.events import CommandExecuted
from yapapi.log import enable_default_logger
from yapapi.payload import vm
from yapapi.rest.activity import CommandExecutionError

examples_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))

from utils import (
    build_parser,
    TEXT_COLOR_CYAN,
    TEXT_COLOR_DEFAULT,
    TEXT_COLOR_GREEN,
    TEXT_COLOR_RED,
    TEXT_COLOR_YELLOW,
)

TEST_TIMEOUT = timedelta(minutes=30)

arg_parser = build_parser("Run ai-benchmark on Golem provider.")
arg_parser.add_argument("--max-workers", type=int, default=1,
    help="The maximum number of nodes we want to run the benchmark on (default is 1)")
arg_parser.add_argument("--min-cpu", type=int, default=2,
    help="The minimum number of cpu cores we want to run the benchmark on (default is 2)")
arg_parser.add_argument("--min-mem", type=int, default=8,
    help="The minimum number of memory in GB we want to run the benchmark on (default is 8)")
args = argparse.Namespace()

async def run_benchmark(ctx: WorkContext, tasks: AsyncIterable[Task]):
    """Invoke ai-benchmark on the target."""
    async for task in tasks:
        ctx.run(f"/benchmark.py")
        output_file="/golem/output/benchmark.log"

        ctx.download_file(output_file, f"benchmark.log")

        yield ctx.commit(timeout=TEST_TIMEOUT)

        with open(output_file) as f:
            result = f.readline()
            if "Score:" in result:
                task.accept_result(result)

async def main(args):
    package = await vm.repo(
        image_hash="bdb2a92a2cc82e3511235634a0341537f04cfd8a4725fdaee983bb65",
        min_mem_gib=args.min_mem,
        min_storage_gib=0.1,
    )

    async with Golem(
        budget=1.0,
        subnet_tag=args.subnet_tag,
        driver=args.driver,
        network=args.network,
    ) as golem:

        print(
            f"Using subnet: {TEXT_COLOR_YELLOW}{args.subnet_tag}{TEXT_COLOR_DEFAULT}, "
            f"payment driver: {TEXT_COLOR_YELLOW}{golem.driver}{TEXT_COLOR_DEFAULT}, "
            f"and network: {TEXT_COLOR_YELLOW}{golem.network}{TEXT_COLOR_DEFAULT}\n"
        )

        start_time = datetime.now()
        data = [Task(data=c) for c in range(0, args.max_workers)]

        completed = golem.execute_tasks(
            run_benchmark,
            data,
            payload=package,
            max_workers=args.max_workers,
            timeout=TEST_TIMEOUT,
        )

        async for task in completed:
            print(
                f"{TEXT_COLOR_CYAN}Task computed: {task}, result: {task.result}{TEXT_COLOR_DEFAULT}"
            )

        print(f"{TEXT_COLOR_CYAN}Total time: {datetime.now() - start_time}{TEXT_COLOR_DEFAULT}")

if __name__ == "__main__":
    args = arg_parser.parse_args()

    enable_default_logger(log_file=args.log_file)

    loop = asyncio.get_event_loop()
    task = loop.create_task(main(args))

    try:
        loop.run_until_complete(task)
    except NoPaymentAccountError as e:
        handbook_url = (
            "https://handbook.golem.network/requestor-tutorials/"
            "flash-tutorial-of-requestor-development"
        )
        print(
            f"{TEXT_COLOR_RED}"
            f"No payment account initialized for driver `{e.required_driver}` "
            f"and network `{e.required_network}`.\n\n"
            f"See {handbook_url} on how to initialize payment accounts for a requestor node."
            f"{TEXT_COLOR_DEFAULT}"
        )
    except KeyboardInterrupt:
        print(
            f"{TEXT_COLOR_YELLOW}"
            "Shutting down gracefully, please wait a short while "
            "or press Ctrl+C to exit immediately..."
            f"{TEXT_COLOR_DEFAULT}"
        )
        task.cancel()
        try:
            loop.run_until_complete(task)
            print(
                f"{TEXT_COLOR_YELLOW}Shutdown completed, thank you for waiting!{TEXT_COLOR_DEFAULT}"
            )
        except KeyboardInterrupt:
            pass
