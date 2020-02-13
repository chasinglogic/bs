"""Class for executing the commands in the DAG"""

import asyncio


class Executor:
    """This is the event loop that dispatches commands"""

    def __init__(self, max_jobs):
        self.max_jobs = max_jobs
        # A queue of commands to run
        self.queue = []
        self.running = False
        self.active_jobs = 0

    def send_job(self, builder):
        self.queue.append(builder)

    def stop(self):
        self.running = False

    async def execute(self, builder):
        for command in builder:
            proc = await self.__run_command(command)
            if proc.exit_code != 0:
                raise Exception(
                    f"""'{command}' exited with code {proc.exit_code}
{proc.stdout.decode()}
{proc.stderr.decode()}
                """
                )

    async def __run_command(self, command):
        return await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )

    async def run(self):
        if not self.running:
            self.running = True

        # TODO this is probably wrong
        while self.running:
            if not self.queue:
                continue

            if self.active_jobs >= self.max_jobs:
                continue

            builder = self.queue.pop()
            self.active_jobs += 1
            proc = await execute(builder)
            self.active_jobs -= 1
